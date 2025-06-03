

package default_pkg ;

`define STR(s) "s"

integer CLK_CYCLE = 10 ;

logic           sys_clk ;
logic           sys_rst ;
logic           sys_rst_n ;
logic [63:0]    sys_clk_cnt ;

task sys_clock_set(integer period);
    CLK_CYCLE = period ;
endtask 

task sys_clock_run();
    forever begin
        sys_clk = 0 ; #(CLK_CYCLE/2) ;
        sys_clk = 1 ; #(CLK_CYCLE/2) ;
    end
endtask 

task sys_count_run();
    forever begin
        @(posedge sys_clk) begin
            if(sys_rst_n == 0) begin
                sys_clk_cnt <= 0 ;
            end else begin
                sys_clk_cnt <= sys_clk_cnt + 1 ;
            end
        end        
    end
endtask 

task sys_delay(
    input [31:0] cycles
);
    #(CLK_CYCLE*cycles) ;
    // for(integer idx=0; idx<cycles; idx=idx+1) begin
    //     #(CLK_CYCLE) ;
    // end
endtask

task sys_reset(
    input [31:0] cycles
);
    sys_rst_n = 0 ;
    sys_rst <= 1 ;
    sys_delay(cycles);
    sys_rst <= 0 ;
    sys_rst_n = 1 ;
endtask 

task sys_info_sim_start();
    printf("---------------------------------");
    printf("Simulation starts to run.", "pink");
    printf("---------------------------------");
endtask 

task sys_info_sim_end();
    printf("---------------------------------");
    printf("Simulation is finished.", "pink");
    printf("---------------------------------");
endtask 

task printf( string text, string color="normal" );
    if( color == "normal" ) begin
        $display( "%s", text );
    end else if (color == "red") begin
        $display("\033[0m\033[1;31m%s\033[0m", text);
    end else if(color == "green")begin
        $display("\033[0m\033[1;32m%s\033[0m", text);
    end else if (color == "yellow") begin
        $display("\033[0m\033[1;33m%s\033[0m", text);
    end else if (color == "blue") begin
        $display("\033[0m\033[1;34m%s\033[0m", text);
    end else if (color == "pink") begin
        $display("\033[0m\033[1;35m%s\033[0m", text);
    end else if (color == "cyan") begin
        $display("\033[0m\033[1;36m%s\033[0m", text);
    end 
endtask
task printf_red(string text);
    $display("\033[0m\033[1;31m%s\033[0m", text);
endtask 
task printf_green(string text);
    $display("\033[0m\033[1;32m%s\033[0m", text);
endtask 
task printf_yellow(string text);
    $display("\033[0m\033[1;33m%s\033[0m", text);
endtask 
task printf_blue(string text);
    $display("\033[0m\033[1;34m%s\033[0m", text);
endtask 
task printf_pink(string text);
    $display("\033[0m\033[1;35m%s\033[0m", text);
endtask 
task printf_cyan(string text);
    $display("\033[0m\033[1;36m%s\033[0m", text);
endtask 

task sys_set_color(string color="normal");
    if( color == "normal" ) begin
        $write( "\033[0m" );
    end else if (color == "red") begin
        $write( "\033[0m\033[1;31m" );
    end else if(color == "green")begin
        $write( "\033[0m\033[1;32m" );
    end else if (color == "yellow") begin
        $write( "\033[0m\033[1;33m" );
    end else if (color == "blue") begin
        $write( "\033[0m\033[1;34m" );
    end else if (color == "pink") begin
        $write( "\033[0m\033[1;35m" );
    end else if (color == "cyan") begin
        $write( "\033[0m\033[1;36m" );
    end 
endtask 
task sys_unset_color();
    $write("\033[0m");
endtask 

function string get_testbench_name(string full_path);
    string module_name;
    int i;
    for (i = 0; i < full_path.len(); i++) begin
        if (full_path[i] == ".") begin
            break; 
        end
        module_name = {module_name, full_path[i]};
    end
    return module_name;
endfunction

endpackage