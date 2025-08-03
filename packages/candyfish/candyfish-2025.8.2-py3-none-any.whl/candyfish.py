import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import re
import math

class HierarchicalAttention(nn.Module):
    """分层动态注意力机制"""
    def __init__(self, embed_size, heads, concept_embed_size=128, concept_vocab_size=1000):
        super(HierarchicalAttention, self).__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads
        self.concept_embed_size = concept_embed_size
        self.concept_vocab_size = concept_vocab_size

        # 字符级注意力
        self.char_values = nn.Linear(embed_size, embed_size)
        self.char_keys = nn.Linear(embed_size, embed_size)
        self.char_queries = nn.Linear(embed_size, embed_size)
        self.char_fc_out = nn.Linear(embed_size, embed_size)

        # 概念级注意力
        self.concept_embedding = nn.Embedding(concept_vocab_size, concept_embed_size)
        self.concept_values = nn.Linear(concept_embed_size, concept_embed_size)
        self.concept_keys = nn.Linear(concept_embed_size, concept_embed_size)
        self.concept_queries = nn.Linear(embed_size, concept_embed_size)
        self.concept_fc_out = nn.Linear(concept_embed_size, embed_size)

        # 融合门控
        self.gate = nn.Linear(embed_size * 2, embed_size)

    def forward(self, values, keys, query, concept_ids=None, mask=None, cache=None):
        N = query.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], query.shape[1]

        # 处理缓存
        if cache is not None:
            # 当有缓存时，我们需要调整查询、键和值
            # 1. 拼接历史键和值
            keys = torch.cat([cache["prev_keys"], keys], dim=1)
            values = torch.cat([cache["prev_values"], values], dim=1)
            # 2. 只关注最后一个位置的查询
            query = query[:, -1:, :]
            # 3. 更新长度
            value_len, key_len = values.shape[1], keys.shape[1]
            query_len = query.shape[1]
            # 4. 调整掩码形状以匹配新的键长度
            if mask is not None:
                # 扩展掩码以匹配键的总长度
                mask = torch.ones((N, 1, query_len, key_len), device=mask.device)
                mask = torch.tril(mask)  # 添加因果掩码

        # 更新缓存
        new_cache = {
            "prev_keys": keys,
            "prev_values": values
        }

        # 字符级注意力
        char_values = self.char_values(values).reshape(N, value_len, self.heads, self.head_dim)
        char_keys = self.char_keys(keys).reshape(N, key_len, self.heads, self.head_dim)
        char_queries = self.char_queries(query).reshape(N, query_len, self.heads, self.head_dim)

        # 确保head_dim是正确的
        if self.head_dim * self.heads != self.embed_size:
            raise ValueError(f"嵌入大小 {self.embed_size} 必须能被头数 {self.heads} 整除")

        char_energy = torch.einsum("nqhd,nkhd->nhqk", [char_queries, char_keys])

        if mask is not None:
            while mask.dim() < 4:
                mask = mask.unsqueeze(1)
            # 确保掩码形状与能量形状匹配
            if mask.shape != char_energy.shape:
                mask = torch.ones((N, 1, query_len, key_len), device=mask.device)
                mask = torch.tril(mask)  # 添加因果掩码
            char_energy = char_energy.masked_fill(mask == 0, float("-1e20"))

        char_attention = torch.softmax(char_energy / (self.embed_size ** (1/2)), dim=3)
        char_out = torch.einsum("nhql,nlhd->nqhd", [char_attention, char_values]).reshape(
            N, query_len, self.heads * self.head_dim
        )
        char_out = self.char_fc_out(char_out)

        # ===== 概念级注意力 =====
        out = char_out  # 默认使用字符级输出
        
        if concept_ids is not None:
            # 当有缓存时，concept_ids只包含当前步骤的概念ID
            if cache is not None and concept_ids.size(1) > query_len:
                concept_ids = concept_ids[:, -query_len:]
                
            # 概念嵌入和投影
            concept_emb = self.concept_embedding(concept_ids)
            
            # 确保概念值、键、查询的维度匹配
            concept_values = self.concept_values(concept_emb)
            concept_keys = self.concept_keys(concept_emb)
            concept_queries = self.concept_queries(query)
            
            # 概念级注意力计算
            concept_energy = torch.einsum("nqhd,nkhd->nhqk", [
                concept_queries.reshape(N, query_len, self.heads, self.head_dim),
                concept_keys.reshape(N, concept_keys.size(1), self.heads, self.head_dim)
            ])
            
            # 掩码处理
            if mask is not None:
                if mask.shape != concept_energy.shape:
                    mask = torch.ones((N, 1, query_len, concept_keys.size(1)), device=mask.device)
                    mask = torch.tril(mask)  # 添加因果掩码
                concept_energy = concept_energy.masked_fill(mask == 0, float("-1e20"))
            
            # 注意力权重和输出
            concept_attention = torch.softmax(concept_energy / (self.embed_size ** (1/2)), dim=3)
            concept_out = torch.einsum("nhql,nlhd->nqhd", [concept_attention, 
                                                          concept_values.reshape(N, concept_values.size(1), self.heads, self.head_dim)])
            concept_out = concept_out.reshape(N, query_len, self.heads * self.head_dim)
            concept_out = self.concept_fc_out(concept_out)
            
            # 融合门控
            # 确保char_out和concept_out的维度匹配
            if char_out.shape != concept_out.shape:
                char_out = char_out[:, :concept_out.size(1), :]
                
            gate = torch.sigmoid(self.gate(torch.cat([char_out, concept_out], dim=-1)))
            out = gate * char_out + (1 - gate) * concept_out
        else:
            # 如果没有概念信息，直接使用字符级输出
            out = char_out
        
        return out, new_cache

class AdvancedTextGeneratorModel(nn.Module):
    """高级文本生成模型"""
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_heads,
                 eos_token_id, concept_vocab_size=1000):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.eos_token_id = eos_token_id

        # 改进的LSTM配置
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=2, 
            batch_first=True, 
            bidirectional=False, 
            dropout=0.2
        )

        # 分层注意力层
        self.hierarchical_attention = HierarchicalAttention(
            hidden_dim, num_heads, 
            concept_embed_size=hidden_dim // 2, 
            concept_vocab_size=concept_vocab_size
        )

        # 层归一化和前馈网络
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Dropout(0.2)
        )

        # 输出层
        self.output_layer = nn.Linear(hidden_dim, vocab_size)

        # 初始化权重
        self._init_weights()

        # 新增特性：自适应残差因子
        self.adaptive_residual = True

        # 概念映射表
        self.concept_map = None

    def _init_weights(self):
        for name, param in self.named_parameters():
            if 'weight' in name:
                if 'lstm' in name:
                    if 'weight_ih' in name:
                        nn.init.xavier_uniform_(param)
                    elif 'weight_hh' in name:
                        nn.init.orthogonal_(param)
                elif 'attention' in name or 'fc' in name or 'output_layer' in name:
                    nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.constant_(param, 0.0)
        nn.init.normal_(self.embedding.weight, mean=0, std=0.01)

    def set_concept_map(self, concept_map):
        """设置概念映射表"""
        self.concept_map = concept_map

    def _get_concept_ids(self, token_ids):
        """将token IDs映射到概念IDs"""
        if self.concept_map is None:
            return None

        batch_size, seq_len = token_ids.shape
        concept_ids = torch.zeros((batch_size, seq_len), dtype=torch.long, device=token_ids.device)

        for i in range(batch_size):
            for j in range(seq_len):
                token_id = token_ids[i, j].item()
                concept_ids[i, j] = self.concept_map.get(token_id, 0)

        return concept_ids

    def _compute_residual_factor(self, hidden_state):
        """计算自适应残差因子"""
        if not self.adaptive_residual:
            return 0.7

        # 基于隐藏状态的标准差计算残差因子
        std = torch.std(hidden_state, dim=(1, 2)).mean()
        factor = torch.clamp(1.0 - std, min=0.3, max=0.9)
        return factor.item()

    def forward(self, x, hidden_state=None, cache=None, mask=None):
        # 嵌入层
        emb = self.embedding(x)

        # LSTM层
        if hidden_state is not None:
            lstm_out, hidden_state = self.lstm(emb, hidden_state)
        else:
            lstm_out, hidden_state = self.lstm(emb)

        # 获取概念IDs
        concept_ids = self._get_concept_ids(x)

        # 分层注意力层
        attn_out, new_cache = self.hierarchical_attention(
            values=lstm_out,
            keys=lstm_out,
            query=lstm_out,
            concept_ids=concept_ids,
            mask=mask,
            cache=cache
        )

        # 自适应残差连接
        residual_factor = self._compute_residual_factor(lstm_out)
        lstm_out = self.norm1(lstm_out + residual_factor * attn_out)

        # 前馈网络
        ff_out = self.fc(lstm_out)
        lstm_out = self.norm2(lstm_out + residual_factor * ff_out)

        # 输出层
        output = self.output_layer(lstm_out)

        return output, hidden_state, new_cache

class Model:
    """模型包装类"""
    def __init__(self, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.vocab = None
        self.char2idx = None
        self.idx2char = None
        self.vocab_size = 0
        self.embedding_dim = 256
        self.attention_heads = 4
        if self.embedding_dim % self.attention_heads != 0:
            self.attention_heads = max(1, self.embedding_dim // 64)
        self.hidden_dim = 1024
        self.max_length = 1024
        self.hidden_state = None
        self.cache = None
        self.concept_map = None
        self.concept_vocab_size = 1000

    def _build_hybrid_vocab(self):
        """构建混合字符集（中文+英文+符号+特殊标记）"""
        # 特殊标记
        self.vocab = [
            '<PAD>', '<UNK>', '<BOS>', '<EOS>', '<|user|>', '<|assistant|>', 
            '<|system|>', '<|think|>', '<|end|>', '<|sep|>', '<|mask|>'
        ]
        
        # 基本ASCII字符 (32-126)
        self.vocab.extend([chr(i) for i in range(32, 127)])
        
        # 常用中文汉字 (Unicode范围)
        self.vocab.extend([chr(i) for i in range(0x4E00, 0x9FA5 + 1)])
        
        # 中文标点符号
        chinese_punctuation = [
            '，', '。', '！', '？', '；', '：', '、', '～', '·', '…', 
            '「', '」', '『', '』', '【', '】', '《', '》', '〈', '〉', 
            '（', '）', '〔', '〕', '〖', '〗', '〘', '〙', '〚', '〛',
            '＂', '＇', '｀', '＾', '＿', '～', '〝', '〞', '–', '—',
            '‘', '’', '“', '”', '„', '‟', '‹', '›', '«', '»'
        ]
        self.vocab.extend(chinese_punctuation)
        
        # 数学符号
        math_symbols = [
            '＋', '－', '×', '÷', '＝', '≠', '≈', '≡', '≤', '≥', 
            '＜', '＞', '≦', '≧', '≮', '≯', '∝', '∞', '√', '∛',
            '∠', '⊥', '∥', '∧', '∨', '∩', '∪', '∫', '∬', '∮',
            '∴', '∵', '∶', '∷', '∼', '≃', '≅', '≈', '≌', '≒',
            '⊕', '⊗', '⊙', '⊖', '⊘', '⊚', '⊛', '⊜', '⊝', '⊞',
            '⊟', '⊠', '⊡', '⊢', '⊣', '⊤', '⊥', '⊦', '⊧', '⊨',
            '⊩', '⊪', '⊫', '⊬', '⊭', '⊮', '⊯', '⊰', '⊱', '⊲',
            '⊳', '⊴', '⊵', '⊶', '⊷', '⊸', '⊹', '⊺', '⊻', '⊼',
            '⊽', '⊾', '⊿', '⋀', '⋁', '⋂', '⋃', '⋄', '⋅', '⋆',
            '⋇', '⋈', '⋉', '⋊', '⋋', '⋌', '⋍', '⋎', '⋏', '⋐',
            '⋑', '⋒', '⋓', '⋔', '⋕', '⋖', '⋗', '⋘', '⋙', '⋚',
            '⋛', '⋜', '⋝', '⋞', '⋟', '⋠', '⋡', '⋢', '⋣', '⋤',
            '⋥', '⋦', '⋧', '⋨', '⋩', '⋪', '⋫', '⋬', '⋭', '⋮',
            '⋯', '⋰', '⋱', '⋲', '⋳', '⋴', '⋵', '⋶', '⋷', '⋸',
            '⋹', '⋺', '⋻', '⋼', '⋽', '⋾', '⋿'
        ]
        self.vocab.extend(math_symbols)
        
        # 货币符号
        currency_symbols = [
            '¥', '€', '$', '¢', '£', '¤', '₣', '₤', '₥', '₦',
            '₧', '₨', '₩', '₪', '₫', '₭', '₮', '₯', '₰', '₱',
            '₲', '₳', '₴', '₵', '₶', '₷', '₸', '₹', '₺', '₻',
            '₼', '₽', '₾', '₿', '꠸', '﷼'
        ]
        self.vocab.extend(currency_symbols)
        
        # 创建映射
        self.char2idx = {char: idx for idx, char in enumerate(self.vocab)}
        self.idx2char = {idx: char for idx, char in enumerate(self.vocab)}
        self.vocab_size = len(self.vocab)
        
        # 打印词汇表信息
        print(f"[词汇表] 已构建混合词汇表，共 {self.vocab_size} 个字符")
        return self.vocab_size

    def new(self, embedding_dim=256, hidden_dim=1024, attention_heads=4, max_length=1024):
        """创建新模型并自动构建混合词汇表"""
        # 自动构建混合词汇表
        self._build_hybrid_vocab()
        
        # 设置模型参数
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.max_length = max_length
        self.attention_heads = attention_heads

        if embedding_dim % attention_heads != 0:
            raise ValueError(f"嵌入维度 {embedding_dim} 必须能被注意力头数 {attention_heads} 整除")
            
        print(f"[模型初始化] 词汇表大小: {self.vocab_size} 嵌入维度: {embedding_dim} 隐藏维度: {hidden_dim} 注意力头数: {attention_heads}")
        
        # 获取EOS标记ID
        eos_token_id = self.char2idx.get('<EOS>', 3)
        
        self.model = AdvancedTextGeneratorModel(
            vocab_size=self.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_heads=self.attention_heads,
            eos_token_id=eos_token_id,
            concept_vocab_size=self.concept_vocab_size
        ).to(self.device)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss(ignore_index=self.char2idx.get('<PAD>', 0)).to(self.device)
        self.reset_state()
        return self

    def reset_state(self):
        """重置模型状态"""
        self.hidden_state = None
        self.cache = None

    def _encode_text(self, text):
        if not self.char2idx:
            raise ValueError("词汇表未初始化")
        
        # 正则匹配特殊标记（如 <|user|>、<|assistant|>）
        special_tokens = re.compile(r'<\|[a-zA-Z]+\|>')
        encoded = []
        i = 0
        
        while i < len(text):
            # 检查是否匹配特殊标记
            match = special_tokens.match(text[i:])
            if match:
                token = match.group(0)
                if token in self.char2idx:
                    encoded.append(self.char2idx[token])
                    i += len(token)
                    continue
                else:
                    print(f"警告: 未知的特殊标记 '{token}'，请添加到词汇表")
                    i += len(token)
                    continue
            
            # 普通字符处理
            char = text[i]
            if char in self.char2idx:
                encoded.append(self.char2idx[char])
            i += 1
        
        return encoded

    def _decode_text(self, indices):
        """解码索引序列为文本"""
        if not self.idx2char:
            raise ValueError("词汇表未初始化")
        return ''.join([self.idx2char.get(idx, '<UNK>') for idx in indices])

    def load_concept_map(self, concept_map_path):
        """加载概念映射表"""
        # 这里简化实现，实际应用中可能需要从文件加载
        self.concept_map = {i: i % self.concept_vocab_size for i in range(self.vocab_size)}
        self.model.set_concept_map(self.concept_map)
        print(f"[概念映射] 已加载 {len(self.concept_map)} 个概念映射")

    def generate(self, prompt, max_length=50, temperature=0.7, use_concept_attention=True, 
             repetition_penalty=1.2, token_penalties=None, stop_strings=None):
        """生成文本
        Args:
            prompt: 输入的提示文本
            max_length: 生成的最大长度
            temperature: 温度参数，控制随机性
            use_concept_attention: 是否使用概念注意力
            repetition_penalty: 重复惩罚系数 (>1时惩罚重复token)
            token_penalties: 指定token的惩罚字典 {token: penalty}
            stop_strings: 自定义停止字符串列表，遇到这些字符串时停止生成
        """
        if self.model is None:
            raise ValueError("模型未初始化")

        # 禁用或启用概念注意力
        self.model.hierarchical_attention.concept_embedding.weight.requires_grad = use_concept_attention

        # 编码提示
        input_seq = self._encode_text(prompt)
        if not input_seq:
            return "请输入有效的提示词"

        generated = []
        # 初始化token出现次数记录
        token_counts = {}
        
        # 初始化停止符相关变量
        stop_sequences = []
        if stop_strings:
            # 将停止字符串编码为token序列
            for stop_str in stop_strings:
                stop_seq = self._encode_text(stop_str)
                if stop_seq:  # 确保编码有效
                    stop_sequences.append(stop_seq)
        
        # 缓存已生成文本用于停止符检测
        generated_text = ""

        with torch.no_grad():
            for i in range(max_length):
                inputs = torch.tensor([input_seq], dtype=torch.long).to(self.device)

                # 创建掩码 - 现在由注意力层内部处理
                mask = None

                # 前向传播
                try:
                    outputs, self.hidden_state, self.cache = self.model(
                        inputs,
                        hidden_state=self.hidden_state,
                        cache=self.cache,
                        mask=mask
                    )
                except RuntimeError as e:
                    print(f"[错误] 前向传播失败: {e}")
                    print(f"[调试信息] 输入形状: {inputs.shape}")
                    if self.hidden_state is not None:
                        print(f"[调试信息] 隐藏状态形状: {self.hidden_state[0].shape}, {self.hidden_state[1].shape}")
                    raise

                last_output = outputs[0, -1, :]

                # 应用重复惩罚和指定token惩罚
                logits = last_output.clone()
                
                # 重复惩罚
                if repetition_penalty != 1.0:
                    for token_id, count in token_counts.items():
                        if count > 0 and logits[token_id] > 0:
                            logits[token_id] /= (repetition_penalty ** count)
                        elif count > 0 and logits[token_id] < 0:
                            logits[token_id] *= (repetition_penalty ** count)
                
                # 指定token惩罚
                if token_penalties:
                    for token, penalty in token_penalties.items():
                        if token in self.char2idx:
                            token_id = self.char2idx[token]
                            if penalty > 1.0:  # 惩罚
                                logits[token_id] /= penalty
                            elif penalty < 1.0:  # 鼓励
                                logits[token_id] *= (1.0 / penalty)

                # 温度缩放和采样
                if temperature > 0:
                    probs = torch.softmax(logits / temperature, dim=-1)
                    
                    # 改进的Top-p (nucleus) 采样
                    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
                    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                    
                    # 移除累积概率小于top_p的标记
                    top_p = 0.95
                    sorted_indices_to_remove = cumulative_probs > top_p
                    # 始终保留第一个标记
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    # 创建掩码并应用于概率
                    indices_to_remove = sorted_indices_to_remove.scatter(
                        0, sorted_indices, sorted_indices_to_remove
                    )
                    filtered_probs = probs.masked_fill(indices_to_remove, 0.0)
                    
                    # 如果所有标记都被移除，回退到原始概率
                    if torch.sum(filtered_probs) > 0:
                        probs = filtered_probs / torch.sum(filtered_probs)
                    else:
                        probs = torch.softmax(logits, dim=-1)
                    
                    next_char_idx = torch.multinomial(probs, 1).item()
                else:
                    # 贪婪采样
                    next_char_idx = torch.argmax(logits).item()

                # 检查结束符
                if next_char_idx == self.char2idx.get('<EOS>', 3):
                    break

                generated.append(next_char_idx)
                input_seq.append(next_char_idx)
                
                # 更新token计数
                token_counts[next_char_idx] = token_counts.get(next_char_idx, 0) + 1
                
                # 更新生成的文本用于停止符检测
                new_char = self.idx2char.get(next_char_idx, '')
                generated_text += new_char

                # 检查自定义停止符
                stop_generation = False
                if stop_sequences:
                    # 检查是否匹配任何停止序列
                    for stop_seq in stop_sequences:
                        # 检查最后几个token是否匹配停止序列
                        if len(input_seq) >= len(stop_seq):
                            recent_tokens = input_seq[-len(stop_seq):]
                            if recent_tokens == stop_seq:
                                stop_generation = True
                                break
                
                if stop_generation:
                    break

                # 截断过长序列
                if len(input_seq) > self.max_length:
                    input_seq = input_seq[-self.max_length:]
                    self.cache = None  # 缓存需要重置
                    
                    # 重新生成文本缓存用于停止符检测
                    generated_text = self._decode_text(input_seq)

        # 解码生成的文本
        return self._decode_text(generated)

    def save(self, save_path):
        """保存模型"""
        if self.model is None or self.vocab is None:
            raise ValueError("模型或词汇表未初始化")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save({
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'vocab': self.vocab,
            'char2idx': self.char2idx,
            'idx2char': self.idx2char,
            'embedding_dim': self.embedding_dim,
            'hidden_dim': self.hidden_dim,
            'max_length': self.max_length,
            'attention_heads': self.attention_heads,
            'concept_vocab_size': self.concept_vocab_size
        }, save_path)
        print(f"[模型] 已保存到 {save_path}")

    def load(self, load_path):
        """加载模型"""
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"模型文件 {load_path} 不存在")

        checkpoint = torch.load(load_path, map_location=self.device)

        # 加载词汇表
        self.vocab = checkpoint['vocab']
        self.char2idx = checkpoint['char2idx']
        self.idx2char = checkpoint['idx2char']
        self.vocab_size = len(self.vocab)

        # 加载模型参数
        self.embedding_dim = checkpoint.get('embedding_dim', 256)
        self.hidden_dim = checkpoint.get('hidden_dim', 1024)
        self.max_length = checkpoint.get('max_length', 1024)
        self.attention_heads = checkpoint.get('attention_heads', 4)
        self.concept_vocab_size = checkpoint.get('concept_vocab_size', 1000)

        # 初始化模型
        eos_token_id = self.char2idx.get('<EOS>', 3)
        self.model = AdvancedTextGeneratorModel(
            vocab_size=self.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_heads=self.attention_heads,
            eos_token_id=eos_token_id,
            concept_vocab_size=self.concept_vocab_size
        ).to(self.device)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss(ignore_index=self.char2idx.get('<PAD>', 0)).to(self.device)

        # 加载模型状态
        try:
            self.model.load_state_dict(checkpoint['model_state'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state'])
            print(f"[模型] 已从 {load_path} 加载")
            return True
        except Exception as e:
            print(f"[错误] 模型加载失败: {e}")
            return False

    def train(self, sample, study_lr=None, epochs=1, batch_size=None):
        """
        训练模型
        
        参数:
        sample - 训练样本，可以是:
            (input_str, target_str) 元组
            或 [(input_str1, target_str1), (input_str2, target_str2)] 列表
        study_lr - 学习率（可选）
        epochs - 训练轮数
        batch_size - 批大小（可选）
        """
        if self.model is None:
            raise ValueError("模型未初始化")
        
        # 设置训练模式
        self.model.train()
        
        # 处理学习率
        if study_lr is not None:
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = study_lr
        
        # 准备样本数据
        if isinstance(sample, tuple):
            samples = [sample]
        else:
            samples = sample
        
        total_loss = 0
        num_batches = 0
        
        for epoch in range(epochs):
            # 打乱样本顺序
            np.random.shuffle(samples)
            
            # 分批处理
            if batch_size is None:
                batch_size = len(samples)
            batches = [samples[i:i+batch_size] for i in range(0, len(samples), batch_size)]
            
            for batch in batches:
                # 重置梯度
                self.optimizer.zero_grad()
                
                # 准备批数据 - 修正训练目标
                batch_inputs = []
                batch_targets = []
                max_len = 0
                
                for sample in batch:
                    context, continuation = sample
                    # 编码输入和输出
                    encoded_ctx = self._encode_text(context)
                    encoded_cont = self._encode_text(continuation)
                    
                    # 修正：全部位置都是有效目标
                    # 输入是整个序列（上下文+续写）
                    input_seq = encoded_ctx + encoded_cont
                    # 目标是输入序列的下一个位置（移位预测）
                    target_seq = input_seq[1:] + [self.char2idx.get('<EOS>', 3)]  # 添加EOS标记
                    input_seq = input_seq[:-1]  # 输入序列去掉最后一个字符
                    
                    # 检查长度一致性
                    if len(input_seq) != len(target_seq):
                        # 如果长度不一致，调整目标序列
                        target_seq = target_seq[:len(input_seq)]
                    
                    batch_inputs.append(input_seq)
                    batch_targets.append(target_seq)
                    max_len = max(max_len, len(input_seq))
                
                # 创建填充后的张量
                padded_inputs = torch.zeros(len(batch), max_len, dtype=torch.long, device=self.device)
                padded_targets = torch.zeros(len(batch), max_len, dtype=torch.long, device=self.device)
                
                for i, (in_seq, tar_seq) in enumerate(zip(batch_inputs, batch_targets)):
                    # 确保输入和目标长度相同
                    min_len = min(len(in_seq), len(tar_seq), max_len)
                    padded_inputs[i, :min_len] = torch.tensor(in_seq[:min_len], device=self.device)
                    padded_targets[i, :min_len] = torch.tensor(tar_seq[:min_len], device=self.device)
                
                # 创建注意力掩码（下三角矩阵）
                attn_mask = torch.tril(torch.ones(1, 1, max_len, max_len, device=self.device))
                
                # 重置隐藏状态和缓存
                self.reset_state()
                
                # 前向传播
                try:
                    outputs, _, _ = self.model(
                        padded_inputs,
                        mask=attn_mask
                    )
                except Exception as e:
                    print(f"训练错误: {e}")
                    print(f"输入形状: {padded_inputs.shape}")
                    print(f"掩码形状: {attn_mask.shape}")
                    raise
                
                # 计算损失 - 只计算实际存在的目标位置
                loss = self.criterion(
                    outputs.view(-1, self.vocab_size),
                    padded_targets.view(-1)
                )
                
                # 反向传播和优化
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
        
        # 返回平均损失
        return total_loss / num_batches if num_batches > 0 else 0.0

    def sliding_window_train(self, text, study_lr=None, epochs=1, window_size=128, stride=64):
        """
        滑动窗口训练长文本
        
        参数:
        text - 要训练的文本
        study_lr - 学习率（可选）
        epochs - 训练轮数
        window_size - 窗口大小
        stride - 滑动步长
        """
        if not text:
            return 0.0
        
        # 编码文本
        encoded = self._encode_text(text)
        
        # 准备样本 - 修正训练目标
        samples = []
        start = 0
        
        while start + window_size < len(encoded):
            # 获取窗口内容
            window = encoded[start:start+window_size]
            # 创建样本（输入=窗口内容，目标=下一个字符序列）
            input_str = self._decode_text(window[:-1])  # 输入不包括最后一个字符
            target_str = self._decode_text(window[1:])  # 目标是输入的下一个字符
            
            samples.append((input_str, target_str))
            
            # 移动到下一个窗口
            start += stride
        
        # 使用train方法训练
        return self.train(samples, study_lr=study_lr, epochs=epochs)