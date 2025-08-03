#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>

namespace py = pybind11;

std::vector<std::vector<int>> nf(const std::vector<double> &lengths,
                                 double batch_max_length) {
    if (lengths.empty() || batch_max_length <= 0) {
        return {};
    }

    std::vector<std::vector<int>> result;
    double current_space = batch_max_length;

    result.emplace_back();

    for (size_t i = 0; i < lengths.size(); i++) {
        if (lengths[i] > batch_max_length) {
            throw std::runtime_error("Item size exceeds batch max length");
        }

        if (lengths[i] > current_space) {
            result.emplace_back();
            current_space = batch_max_length;
        }

        result.back().push_back(i);
        current_space -= lengths[i];
    }

    return result;
}

PYBIND11_MODULE(nf, m) {
    m.doc() = "NF (Next Fit) algorithm implementation in C++";
    m.def("nf", &nf, "NF algorithm");
}
