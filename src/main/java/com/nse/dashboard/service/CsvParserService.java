package com.nse.dashboard.service;

import com.nse.dashboard.model.OptionData;
import com.nse.dashboard.model.ParticipantData;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

@Service
public class CsvParserService {

    public List<OptionData> parseOptionCsv(MultipartFile file) throws Exception {

        List<OptionData> list = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()));

        String line;
        boolean header = true;

        while ((line = reader.readLine()) != null) {

            if (header) {
                header = false;
                continue;
            }

            String[] cols = line.split(",");

            OptionData d = new OptionData();

            d.setStrike(Double.parseDouble(cols[0]));
            d.setCallOI(Long.parseLong(cols[1]));
            d.setCallBuiltUp(cols[2]);
            d.setPutOI(Long.parseLong(cols[3]));
            d.setPutBuiltUp(cols[4]);
            d.setPcr(Double.parseDouble(cols[5]));

            list.add(d);
        }

        return list;
    }

    public List<ParticipantData> parseParticipantCsv(MultipartFile file) throws Exception {

        List<ParticipantData> list = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()));

        String line;
        boolean header = true;

        while ((line = reader.readLine()) != null) {

            if (header) {
                header = false;
                continue;
            }

            String[] cols = line.split(",");

            ParticipantData d = new ParticipantData();

            d.setCategory(cols[0]);
            d.setBuyValue(Double.parseDouble(cols[1]));
            d.setSellValue(Double.parseDouble(cols[2]));
            d.setNetValue(Double.parseDouble(cols[3]));

            list.add(d);
        }

        return list;
    }
}
