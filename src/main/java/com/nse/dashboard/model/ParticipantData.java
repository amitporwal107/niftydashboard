package com.nse.dashboard.model;

import lombok.Data;

@Data
public class ParticipantData {
    private String category;
    private double buyValue;
    private double sellValue;
    private double netValue;
}
