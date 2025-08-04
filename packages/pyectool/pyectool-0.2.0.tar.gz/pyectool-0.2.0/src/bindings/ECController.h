#pragma once
#include <stdexcept>
#include <string>
#include <vector>
#include "libectool.h"

class ECController {
public:
    int hello();

    bool is_on_ac();
    ec_charge_state_info get_charge_state();

    int get_num_fans();
    void enable_fan_auto_ctrl(int fan_idx);
    void enable_all_fans_auto_ctrl();
    void set_fan_duty(int percent, int fan_idx);
    void set_all_fans_duty(int percent);
    void set_fan_rpm(int target_rpm, int fan_idx);
    void set_all_fans_rpm(int target_rpm);
    int get_fan_rpm(int fan_idx);
    std::vector<int> get_all_fans_rpm();

    int get_num_temp_sensors();
    int get_temp(int sensor_idx);
    std::vector<int> get_all_temps();
    int get_max_temp();
    int get_max_non_battery_temp();
    ec_temp_info get_temp_info(int sensor_idx);

private:
    void handle_error(int code, const std::string &msg);
};
