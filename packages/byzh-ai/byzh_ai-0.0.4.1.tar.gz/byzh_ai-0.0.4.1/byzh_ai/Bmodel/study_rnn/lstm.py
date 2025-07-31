import torch
import torch.nn as nn
import torch.nn.functional as F


class OneLayer_LSTM(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        # Input to hidden
        self.W_ih = nn.Parameter(torch.randn(4 * hidden_size, input_size)) # [4H, C]
        # Hidden to hidden
        self.W_hh = nn.Parameter(torch.randn(4 * hidden_size, hidden_size)) # [4H, H]
        self.b = nn.Parameter(torch.zeros(4 * hidden_size)) # [4H]

    def forward(self, x, state=None):
        # x: [L, B, C]
        seq_len, batch_size, input_size = x.shape

        # h: [B, H]
        # c: [B, H]
        if state is None:
            h_t = torch.zeros(batch_size, self.hidden_size, device=x.device)
            c_t = torch.zeros(batch_size, self.hidden_size, device=x.device)
        else:
            h_t, c_t = state

        outputs = []
        for t in range(seq_len):
            x_t = x[t] # [B, C]
            gates = x_t @ self.W_ih.T + h_t @ self.W_hh.T + self.b # [B, 4H]

            # .chunk将张量沿着指定维度分割成多个相等大小的块, 需要制定块数
            i, f, g, o = gates.chunk(4, dim=1) # i, f, g, o: [B, H]

            i = torch.sigmoid(i) # 输入门(input gate)
            f = torch.sigmoid(f) # 遗忘门(forget gate)
            g = torch.tanh(g)    # 候选记忆(cell gate)
            o = torch.sigmoid(o) # 输出门(output gate)

            c_t = f * c_t + i * g # [B, H]
            h_t = o * torch.tanh(c_t) # [B, H]

            outputs.append(h_t)

        return torch.stack(outputs, dim=0), (h_t, c_t)



class Layers_LSTM(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=False):
        '''
        如果batch_first=False, 输入的x的形状为[L, B, C]

        如果batch_first=True, 输入的x的形状为[B, L, C]
        '''
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first

        self.W_ih_list = nn.ModuleList() # [C, 4H], [H, 4H], [H, 4H], ...
        self.W_hh_list = nn.ModuleList() # [H, 4H], [H, 4H], [H, 4H], ...
        self.b_list = nn.ParameterList() # 4H, 4H, 4H, ......
        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size
            self.W_ih_list.append(nn.Linear(in_size, 4 * hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, 4 * hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(4 * hidden_size)))

    def forward(self, x, state=None):
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # h_t: [B, H] * layer
        # c_t: [B, H] * layer
        if state is None:
            h_t = [torch.zeros(batch_size, self.hidden_size, device=x.device) for _ in range(self.num_layers)]
            c_t = [torch.zeros(batch_size, self.hidden_size, device=x.device) for _ in range(self.num_layers)]
        else:
            h_t = list(torch.unbind(state[0], dim=0))
            c_t = list(torch.unbind(state[1], dim=0))

        layer_input = x
        for layer in range(self.num_layers):
            outputs = []
            h = h_t[layer] # [B, H]
            c = c_t[layer] # [B, H]
            for t in range(seq_len):
                x_t = layer_input[t] # [B, C]
                gates = (
                    self.W_ih_list[layer](x_t) # [B, C] * [C, 4H] -> [B, 4H]
                    + self.W_hh_list[layer](h) # [B, H] * [H, 4H] -> [B, 4H]
                    + self.b_list[layer] # 4H -> [B, 4H]
                )
                i, f, g, o = gates.chunk(4, dim=1) # i, f, g, o: [B, H]

                i = torch.sigmoid(i) # 输入门(input gate)
                f = torch.sigmoid(f) # 遗忘门(forget gate)
                g = torch.tanh(g)    # 候选记忆(cell gate)
                o = torch.sigmoid(o) # 输出门(output gate)

                h = o * torch.tanh(c) # [B, H]
                c = f * c + i * g     # [B, H]
                outputs.append(h)
            layer_input = torch.stack(outputs, dim=0)
            # 更新状态h_t, c_t
            h_t[layer] = h
            c_t[layer] = c

        h_n = torch.stack(h_t, dim=0)
        c_n = torch.stack(c_t, dim=0)

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, (h_n, c_n)


if __name__ == '__main__':
    seq_len, batch_size, input_size, hidden_size, num_layers = 7, 4, 8, 16, 3
    x = torch.randn(seq_len, batch_size, input_size)

    # OneLayer_LSTM
    lstm = OneLayer_LSTM(input_size, hidden_size)
    lstm_out, (h_n, c_n) = lstm(x)
    print("OneLayer_LSTM output:", lstm_out.shape)  # [seq_len, batch, hidden_size]

    # Layers_LSTM
    lstm = Layers_LSTM(input_size, hidden_size, num_layers)
    out_lstm, (h_n_lstm, c_n_lstm) = lstm(x)
    print("Layers_LSTM output:", out_lstm.shape)  # [seq_len, batch, hidden_size]