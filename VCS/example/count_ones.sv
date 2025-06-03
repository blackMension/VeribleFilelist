/*
 * @Author: ZhangShen
 * @Date: 2024-07-15 20:18:20
 * @LastEditors: ZhangShen
 * @LastEditTime: 2024-07-16 20:59:20
 * @Description: 
 * @Created by RICL of ShanghaiTech SIST
 * @FilePath: /SNN/TSNN-HDL/src/Common/count_ones.sv
*/

module count_ones #(
    parameter WIDTH_IN = 8,
    parameter WIDTH_OUT = $clog2(WIDTH_IN+1)
)(
    input [WIDTH_IN-1:0] data_in, // 参数化宽度的输入二进制序列
    output [WIDTH_OUT-1:0] count // 输出1的个数
);

wire [WIDTH_OUT-1:0] temp_count [(WIDTH_IN/2)-1:0];

genvar i;

// 第一阶段：每两位计算一次1的个数
generate
    for (i = 0; i < WIDTH_IN/2; i = i + 1) begin : first_stage
        assign temp_count[i] = (data_in[2*i +: 2] == 2'b00) ? 0 :
                               (data_in[2*i +: 2] == 2'b01) ? 1 :
                               (data_in[2*i +: 2] == 2'b10) ? 1 : 2;
    end
endgenerate

// 第二阶段：对中间结果进行求和
reg [WIDTH_OUT-1:0] sum;
integer j;

always @(*) begin
    sum = 0;
    for (j = 0; j < WIDTH_IN/2; j = j + 1) begin
        sum = sum + temp_count[j];
    end
end

assign count = sum;

endmodule
