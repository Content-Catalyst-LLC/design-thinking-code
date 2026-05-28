use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct ServiceStage {
    name: String,
    completion_probability: f64,
    clarity: f64,
    trust: f64,
    accessibility: f64,
    user_burden: f64,
    staff_load: f64,
    recovery_quality: f64,
}

#[derive(Debug)]
struct ScoredStage {
    name: String,
    quality: f64,
    priority: f64,
    completion_probability: f64,
}

fn quality(x: &ServiceStage) -> f64 {
    0.22 * x.completion_probability * 10.0
        + 0.18 * x.clarity
        + 0.18 * x.trust
        + 0.16 * x.accessibility
        + 0.14 * x.recovery_quality
        - 0.07 * x.user_burden
        - 0.05 * x.staff_load
}

fn priority(x: &ServiceStage) -> f64 {
    let failure_risk = 1.0 - x.completion_probability;
    let burden_risk = 0.55 * x.user_burden + 0.45 * x.staff_load;
    0.34 * failure_risk * 10.0
        + 0.26 * burden_risk
        + 0.18 * (10.0 - x.clarity)
        + 0.12 * (10.0 - x.accessibility)
        + 0.10 * (10.0 - x.recovery_quality)
}

fn parse_stages(path: &str) -> Result<Vec<ServiceStage>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut stages = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 10 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        stages.push(ServiceStage {
            name: fields[0].trim().to_string(),
            completion_probability: fields[3].trim().parse()?,
            clarity: fields[4].trim().parse()?,
            trust: fields[5].trim().parse()?,
            accessibility: fields[6].trim().parse()?,
            user_burden: fields[7].trim().parse()?,
            staff_load: fields[8].trim().parse()?,
            recovery_quality: fields[9].trim().parse()?,
        });
    }

    Ok(stages)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/service_journey_stages_raw.csv".to_string());

    let stages = parse_stages(&path)?;
    let reliability: f64 = stages.iter().map(|s| s.completion_probability).product();

    let mut scored: Vec<ScoredStage> = stages
        .iter()
        .map(|x| ScoredStage {
            name: x.name.clone(),
            quality: quality(x),
            priority: priority(x),
            completion_probability: x.completion_probability,
        })
        .collect();

    scored.sort_by(|a, b| b.priority.partial_cmp(&a.priority).unwrap());

    println!("end_to_end_reliability,{:.8}", reliability);
    println!("rank,stage,service_stage_quality,redesign_priority,completion_probability");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.quality,
            row.priority,
            row.completion_probability
        );
    }

    Ok(())
}
