cmake_minimum_required(VERSION 3.14)
project(yaal)

include(CPM.cmake)
CPMAddPackage("gh:taocpp/PEGTL#3.2.8")



add_executable(yaal yaal.cpp)

target_link_libraries(yaal PRIVATE taocpp::pegtl)
target_compile_features(yaal PRIVATE cxx_std_17)

