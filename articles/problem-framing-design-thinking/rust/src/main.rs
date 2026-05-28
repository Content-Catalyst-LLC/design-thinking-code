use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct ProblemFrame {
    name: String,
    explanatory_adequacy: f64,
    stakeholder_coverage: f64,
    opportunity_value: f64,
    framing_risk: f64,
}

#[derive(Debug)]
struct ScoredFrame {
    name: String,
    value: f64,
}

fn frame_value(frame: &ProblemFrame) -> f64 {
    0.30 * frame.explanatory_adequacy
        + 0.25 * frame.stakeholder_coverage
        + 0.30 * frame.opportunity_value
        - 0.15 * frame.framing_risk
}

fn parse_frames(path: &str) -> Result<Vec<ProblemFrame>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut frames = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 5 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        frames.push(ProblemFrame {
            name: fields[0].trim().to_string(),
            explanatory_adequacy: fields[1].trim().parse()?,
            stakeholder_coverage: fields[2].trim().parse()?,
            opportunity_value: fields[3].trim().parse()?,
            framing_risk: fields[4].trim().parse()?,
        });
    }

    Ok(frames)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/problem_frames_raw.csv".to_string());

    let frames = parse_frames(&path)?;
    let mut scored: Vec<ScoredFrame> = frames
        .iter()
        .map(|f| ScoredFrame {
            name: f.name.clone(),
            value: frame_value(f),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,frame,frame_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
