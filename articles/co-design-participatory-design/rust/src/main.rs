use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct CodesignActivity {
    name: String,
    representation: f64,
    accessibility: f64,
    participant_influence: f64,
    trust_quality: f64,
    evidence_quality: f64,
    implementation_accountability: f64,
    decision_impact: f64,
    ethical_risk: f64,
}

#[derive(Debug)]
struct ScoredActivity {
    name: String,
    quality: f64,
    ethical_risk: f64,
}

fn participation_quality(x: &CodesignActivity) -> f64 {
    0.18 * x.representation
        + 0.14 * x.accessibility
        + 0.22 * x.participant_influence
        + 0.12 * x.trust_quality
        + 0.12 * x.evidence_quality
        + 0.12 * x.implementation_accountability
        + 0.14 * x.decision_impact
        - 0.08 * x.ethical_risk
}

fn parse_activities(path: &str) -> Result<Vec<CodesignActivity>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut activities = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 11 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        activities.push(CodesignActivity {
            name: fields[0].trim().to_string(),
            representation: fields[3].trim().parse()?,
            accessibility: fields[4].trim().parse()?,
            participant_influence: fields[5].trim().parse()?,
            trust_quality: fields[6].trim().parse()?,
            evidence_quality: fields[7].trim().parse()?,
            implementation_accountability: fields[8].trim().parse()?,
            decision_impact: fields[9].trim().parse()?,
            ethical_risk: fields[10].trim().parse()?,
        });
    }

    Ok(activities)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/codesign_activities_raw.csv".to_string());

    let activities = parse_activities(&path)?;
    let mut scored: Vec<ScoredActivity> = activities
        .iter()
        .map(|x| ScoredActivity {
            name: x.name.clone(),
            quality: participation_quality(x),
            ethical_risk: x.ethical_risk,
        })
        .collect();

    scored.sort_by(|a, b| b.quality.partial_cmp(&a.quality).unwrap());

    println!("rank,activity,participation_quality,ethical_risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.quality, row.ethical_risk);
    }

    Ok(())
}
