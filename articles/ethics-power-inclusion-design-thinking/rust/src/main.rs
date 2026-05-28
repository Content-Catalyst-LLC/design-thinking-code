use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct DesignDecision {
    name: String,
    harm: f64,
    probability: f64,
    exposure: f64,
    detectability: f64,
    accountability: f64,
    inclusion: f64,
    public_value: f64,
    repairability: f64,
    privacy: f64,
    autonomy: f64,
    manipulation: f64,
}

#[derive(Debug)]
struct ScoredDecision {
    name: String,
    ethical_risk: f64,
    review_priority: f64,
}

fn ethical_risk(x: &DesignDecision) -> f64 {
    x.harm * x.probability * x.exposure * (1.0 - x.detectability) * (1.0 - x.accountability)
}

fn review_priority(x: &DesignDecision) -> f64 {
    let risk = ethical_risk(x);
    let repair_deficit = 1.0 - x.repairability;
    0.32 * risk
        + 0.20 * x.harm
        + 0.14 * x.exposure
        + 0.10 * (1.0 - x.accountability)
        + 0.08 * (1.0 - x.detectability)
        + 0.06 * (1.0 - x.inclusion)
        + 0.05 * x.privacy
        + 0.03 * x.autonomy
        + 0.02 * x.manipulation
        - 0.12 * x.public_value
        + 0.10 * repair_deficit
}

fn parse_decisions(path: &str) -> Result<Vec<DesignDecision>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut items = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 13 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        items.push(DesignDecision {
            name: fields[0].trim().to_string(),
            harm: fields[2].trim().parse()?,
            probability: fields[3].trim().parse()?,
            exposure: fields[4].trim().parse()?,
            detectability: fields[5].trim().parse()?,
            accountability: fields[6].trim().parse()?,
            inclusion: fields[7].trim().parse()?,
            public_value: fields[8].trim().parse()?,
            repairability: fields[9].trim().parse()?,
            privacy: fields[10].trim().parse()?,
            autonomy: fields[11].trim().parse()?,
            manipulation: fields[12].trim().parse()?,
        });
    }

    Ok(items)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/ethical_design_decisions_raw.csv".to_string());

    let decisions = parse_decisions(&path)?;

    let mut scored: Vec<ScoredDecision> = decisions
        .iter()
        .map(|x| ScoredDecision {
            name: x.name.clone(),
            ethical_risk: ethical_risk(x),
            review_priority: review_priority(x),
        })
        .collect();

    scored.sort_by(|a, b| b.review_priority.partial_cmp(&a.review_priority).unwrap());

    println!("rank,design_decision,ethical_risk,review_priority");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.ethical_risk,
            row.review_priority
        );
    }

    Ok(())
}
