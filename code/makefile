

all:run
module:_trace_dat.so

_trace_dat.so:trace_dat.cpp trace_dat_wrap.cxx
	g++ -shared -fPIC -I/usr/include/python3.6m -lpython3.6m -o _trace_dat.so trace_dat.cpp trace_dat_wrap.cxx

trace_dat_wrap.cxx:trace_dat.i trace_dat.cpp 
	swig -c++ -python -py3 trace_dat.i

run:trace_dat
	./trace_dat


trace_dat:trace_dat.cpp trace_dat.h
	g++ -o trace_dat trace_dat.cpp
