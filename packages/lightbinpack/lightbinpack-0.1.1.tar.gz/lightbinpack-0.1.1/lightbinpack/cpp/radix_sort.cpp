#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <vector>

namespace py = pybind11;

inline int get_value(const std::vector<std::vector<int>> &row, int pos) {
    const auto &primary_list = row[0];
    if (pos < (int)primary_list.size()) {
        return primary_list[pos];
    }
    return 0;
}

void counting_sort_by_position(
    std::vector<std::vector<std::vector<int>>> &data,
    std::vector<std::vector<std::vector<int>>> &output, int pos,
    int max_value) {
    int n = (int)data.size();
    std::vector<int> count(max_value + 1, 0);

    for (int i = 0; i < n; ++i) {
        int val = get_value(data[i], pos);
        ++count[val];
    }

    for (int i = 1; i <= max_value; ++i) {
        count[i] += count[i - 1];
    }

    for (int i = n - 1; i >= 0; --i) {
        int val = get_value(data[i], pos);
        int idx = count[val] - 1;
        output[idx] = std::move(data[i]);
        --count[val];
    }

    data.swap(output);
}

std::vector<std::vector<std::vector<int>>>
radix_sort(const std::vector<std::vector<std::vector<int>>> &input_data,
           int start_index, int max_index, int max_value) {
    if (input_data.empty()) {
        return {};
    }

    std::vector<std::vector<std::vector<int>>> data = input_data;
    int n = (int)data.size();
    std::vector<std::vector<std::vector<int>>> output(n);

    for (int pos = max_index; pos >= start_index; --pos) {
        counting_sort_by_position(data, output, pos, max_value);
    }

    return data;
}

PYBIND11_MODULE(radix_sort, m) {
    m.doc() = "Radix sort implementation for integer lists";
    m.def("radix_sort", &radix_sort,
          "Radix sort algorithm for sorting integer lists",
          py::arg("input_data"), py::arg("start_index") = 0,
          py::arg("max_index") = 32, py::arg("max_value") = 16384);
}
