
topmodule:= template_tb

SIM_THREADS=1
CORENUM=1
CURRENT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ROOT_DIR := $(abspath $(CURRENT_DIR)/../)
FILELIST=./filelist/$(topmodule).f

# TODO: change it to the path of your source codes
SEARCH_PATH=$(abspath $(CURRENT_DIR)/example)

Mdir=./csrc
makeDirs= mkdir -p out log csrc

vcsDefines := \
	+define+ROOT_DIR=\"$(ROOT_DIR)\" \
	+define+USE_VCS_SIMULATION

vcsFiles := 	-l ./log/compile.log \
				-o ./out/simv \
				-f $(FILELIST) 

vcsBaseCommand = 	vcs -full64 \
					$(vcsDefines)\
					+v2k \
					-xlrm module_xmr \
					-sverilog \
					-Mdir=$(Mdir) \
					-kdb \
					-debug_access \
					+lint=TFIPC-L \
					-top  $(topmodule) \
					-j $(CORENUM) \
					-timescale=1ps/1ps

vcsCompileCommand = $(vcsBaseCommand) $(vcsFiles)

make_filelist:
	python ../VeribleFilelist/main.py -t $(topmodule) -s ${SEARCH_PATH} -d "${vcsDefines}"

lint: make_filelist
	$(makeDirs)

compile: lint 
	$(vcsCompileCommand)

compile_gui: lint
	$(vcsCompileCommand) -debug_access+all

compile_fgp: lint
	$(vcsCompileCommand) -fgp

compile_prof: lint
	$(vcsCompileCommand) -simprofile -debug_access+pp

run:
	./out/simv -l log/run.log

run_gui:
	./out/simv -gui

run_fgp:
	./out/simv -l log/run.log -fgp=num_threads:$(SIM_THREADS), allow_less_cores, multisocket, sync:busywait, auto_affinity -xdprof=diag:ruse, -Xdprof=timeline 

run_prof:
	./out/simv -l log/run.log +prof

clean:
	rm -rf simv* *.log *.vpd *.dump csrc *.sim *.mra *.log ucli.key session* *.db vcs.key out/simv* tmp DVEfiles  temp $(Mdir)

remove:
	rm -rf out/*.vcd out/verdi_config_file log/*.log

clear:
	rm -rf ./out ./log ./csrc