#include "test_framework.hpp"

int main() {
    g_test_framework.run_all();
    return g_test_framework.get_exit_code();
}