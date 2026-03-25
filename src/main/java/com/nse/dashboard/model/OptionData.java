package com.nse.dashboard.model;

import lombok.Data;

@Data
public class OptionData {
    private double strike;
    private long callOI;
    private String callBuiltUp;
    private long putOI;
    private String putBuiltUp;
    private double pcr;
}
