use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct ResearchSignal {
    name: String,
    source_strength: f64,
    relevance: f64,
    traceability: f64,
    representativeness: f64,
    validation: f64,
    missingness: f64,
    ai_assistance_risk: f64,
    decision_relevance: f64,
    recency: f64,
    consent: f64,
    coverage: f64,
}

#[derive(Debug)]
struct ScoredSignal {
    name: String,
    confidence: f64,
    bias_risk: f64,
    ai_risk: f64,
    decision_readiness: f64,
    governance_priority: f64,
}

fn clamp01(x: f64) -> f64 {
    x.max(0.0).min(1.0)
}

fn confidence(x: &ResearchSignal) -> f64 {
    0.18*x.source_strength + 0.17*x.relevance + 0.15*x.traceability +
    0.15*x.representativeness + 0.15*x.validation + 0.08*x.recency +
    0.07*x.consent + 0.05*x.coverage
}

fn bias_risk(x: &ResearchSignal) -> f64 {
    0.26*x.missingness + 0.22*(1.0-x.representativeness) +
    0.18*(1.0-x.validation) + 0.14*x.ai_assistance_risk +
    0.10*(1.0-x.traceability) + 0.10*(1.0-x.coverage)
}

fn ai_risk(x: &ResearchSignal) -> f64 {
    0.38*x.ai_assistance_risk + 0.18*(1.0-x.traceability) +
    0.16*(1.0-x.validation) + 0.14*x.missingness + 0.14*(1.0-x.consent)
}

fn decision_readiness(x: &ResearchSignal) -> f64 {
    let c = confidence(x);
    let b = bias_risk(x);
    clamp01(0.30*c + 0.24*x.decision_relevance + 0.14*x.validation +
            0.12*x.traceability + 0.08*x.consent + 0.08*x.coverage - 0.04*b)
}

fn parse_signals(path: &str) -> Result<Vec<ResearchSignal>, Box<dyn Error>> {
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

        items.push(ResearchSignal {
            name: fields[0].trim().to_string(),
            source_strength: fields[2].trim().parse()?,
            relevance: fields[3].trim().parse()?,
            traceability: fields[4].trim().parse()?,
            representativeness: fields[5].trim().parse()?,
            validation: fields[6].trim().parse()?,
            missingness: fields[7].trim().parse()?,
            ai_assistance_risk: fields[8].trim().parse()?,
            decision_relevance: fields[9].trim().parse()?,
            recency: fields[10].trim().parse()?,
            consent: fields[11].trim().parse()?,
            coverage: fields[12].trim().parse()?,
        });
    }

    Ok(items)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/research_signals_raw.csv".to_string());

    let signals = parse_signals(&path)?;

    let mut scored: Vec<ScoredSignal> = signals
        .iter()
        .map(|x| {
            let c = confidence(x);
            let b = bias_risk(x);
            let a = ai_risk(x);
            let d = decision_readiness(x);
            let g = 0.24*b + 0.22*a + 0.16*(1.0-x.traceability) +
                    0.14*(1.0-x.consent) + 0.12*(1.0-x.validation) +
                    0.12*x.decision_relevance;
            ScoredSignal {
                name: x.name.clone(),
                confidence: c,
                bias_risk: b,
                ai_risk: a,
                decision_readiness: d,
                governance_priority: g,
            }
        })
        .collect();

    scored.sort_by(|a, b| b.governance_priority.partial_cmp(&a.governance_priority).unwrap());

    println!("rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness,governance_priority");
    for (idx, row) in scored.iter().enumerate() {
        println!(
            "{},{},{:.6},{:.6},{:.6},{:.6},{:.6}",
            idx + 1,
            row.name,
            row.confidence,
            row.bias_risk,
            row.ai_risk,
            row.decision_readiness,
            row.governance_priority
        );
    }

    Ok(())
}
