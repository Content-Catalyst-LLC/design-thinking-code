use std::collections::HashMap;
use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug)]
struct ThemeAggregate {
    evidence_units: usize,
    total_strength: f64,
    total_risk: f64,
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/contextual_inquiry_evidence_units_raw.csv".to_string());

    let content = fs::read_to_string(path)?;
    let mut aggregates: HashMap<String, ThemeAggregate> = HashMap::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 7 {
            continue;
        }

        let theme = fields[3].trim().to_string();
        let strength: f64 = fields[5].trim().parse()?;
        let risk: f64 = fields[6].trim().parse()?;

        let entry = aggregates.entry(theme).or_insert(ThemeAggregate {
            evidence_units: 0,
            total_strength: 0.0,
            total_risk: 0.0,
        });

        entry.evidence_units += 1;
        entry.total_strength += strength;
        entry.total_risk += risk;
    }

    let mut rows: Vec<(String, usize, f64)> = aggregates
        .iter()
        .map(|(theme, agg)| {
            let mean_strength = agg.total_strength / agg.evidence_units as f64;
            let mean_risk = agg.total_risk / agg.evidence_units as f64;
            let confidence = 0.70 * mean_strength - 0.30 * mean_risk;
            (theme.clone(), agg.evidence_units, confidence)
        })
        .collect();

    rows.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap());

    println!("rank,theme,evidence_units,synthesis_confidence");
    for (rank, row) in rows.iter().enumerate() {
        println!("{},{},{},{:.6}", rank + 1, row.0, row.1, row.2);
    }

    Ok(())
}
