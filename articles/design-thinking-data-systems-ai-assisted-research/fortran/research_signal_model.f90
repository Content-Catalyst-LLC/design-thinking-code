program research_signal_model
  implicit none

  integer, parameter :: n = 10
  character(len=160) :: names(n)
  real(8) :: source_strength(n), relevance(n), traceability(n), representativeness(n), validation(n)
  real(8) :: missingness(n), ai_assistance(n), decision_relevance(n), recency(n), consent(n), coverage(n)
  real(8) :: confidence(n), bias_risk(n), ai_risk(n), readiness(n), governance_priority(n)
  integer :: i

  names = [ character(len=160) :: &
    "Application abandonment at documentation step", &
    "Low trust in eligibility explanations", &
    "Disabled users need assisted access", &
    "Limited-English users misinterpret status messages", &
    "Frontline staff repair data errors manually", &
    "Prototype improves next-step comprehension", &
    "AI summary misses severe edge-case failures", &
    "Service log shows repeat contact after rejection", &
    "Research repository lacks consent metadata", &
    "Semantic search over-retrieves outdated findings" ]

  source_strength = [0.78d0,0.68d0,0.74d0,0.70d0,0.66d0,0.76d0,0.60d0,0.72d0,0.82d0,0.70d0]
  relevance = [0.90d0,0.86d0,0.92d0,0.82d0,0.80d0,0.84d0,0.88d0,0.78d0,0.86d0,0.76d0]
  traceability = [0.82d0,0.76d0,0.80d0,0.74d0,0.70d0,0.78d0,0.66d0,0.72d0,0.88d0,0.68d0]
  representativeness = [0.70d0,0.58d0,0.54d0,0.56d0,0.62d0,0.68d0,0.48d0,0.74d0,0.66d0,0.60d0]
  validation = [0.66d0,0.62d0,0.70d0,0.64d0,0.58d0,0.76d0,0.52d0,0.68d0,0.74d0,0.58d0]
  missingness = [0.32d0,0.42d0,0.46d0,0.44d0,0.38d0,0.30d0,0.54d0,0.34d0,0.40d0,0.44d0]
  ai_assistance = [0.18d0,0.42d0,0.36d0,0.38d0,0.30d0,0.24d0,0.76d0,0.28d0,0.34d0,0.62d0]
  decision_relevance = [0.90d0,0.86d0,0.92d0,0.82d0,0.78d0,0.84d0,0.88d0,0.76d0,0.90d0,0.74d0]
  recency = [0.84d0,0.78d0,0.80d0,0.76d0,0.74d0,0.88d0,0.82d0,0.80d0,0.86d0,0.52d0]
  consent = [0.86d0,0.82d0,0.88d0,0.84d0,0.80d0,0.86d0,0.78d0,0.84d0,0.52d0,0.78d0]
  coverage = [0.72d0,0.60d0,0.58d0,0.62d0,0.66d0,0.70d0,0.50d0,0.76d0,0.68d0,0.64d0]

  do i = 1, n
    confidence(i) = 0.18d0 * source_strength(i) + 0.17d0 * relevance(i) + &
                    0.15d0 * traceability(i) + 0.15d0 * representativeness(i) + &
                    0.15d0 * validation(i) + 0.08d0 * recency(i) + &
                    0.07d0 * consent(i) + 0.05d0 * coverage(i)

    bias_risk(i) = 0.26d0 * missingness(i) + 0.22d0 * (1.0d0 - representativeness(i)) + &
                   0.18d0 * (1.0d0 - validation(i)) + 0.14d0 * ai_assistance(i) + &
                   0.10d0 * (1.0d0 - traceability(i)) + 0.10d0 * (1.0d0 - coverage(i))

    ai_risk(i) = 0.38d0 * ai_assistance(i) + 0.18d0 * (1.0d0 - traceability(i)) + &
                 0.16d0 * (1.0d0 - validation(i)) + 0.14d0 * missingness(i) + &
                 0.14d0 * (1.0d0 - consent(i))

    readiness(i) = max(0.0d0, min(1.0d0, 0.30d0 * confidence(i) + 0.24d0 * decision_relevance(i) + &
                    0.14d0 * validation(i) + 0.12d0 * traceability(i) + 0.08d0 * consent(i) + &
                    0.08d0 * coverage(i) - 0.04d0 * bias_risk(i)))

    governance_priority(i) = 0.24d0 * bias_risk(i) + 0.22d0 * ai_risk(i) + &
                             0.16d0 * (1.0d0 - traceability(i)) + &
                             0.14d0 * (1.0d0 - consent(i)) + &
                             0.12d0 * (1.0d0 - validation(i)) + &
                             0.12d0 * decision_relevance(i)
  end do

  call sort_desc(names, confidence, bias_risk, ai_risk, readiness, governance_priority, n)

  print '(a)', 'rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness,governance_priority'
  do i = 1, n
    print '(i0,a,a,a,f7.4,a,f7.4,a,f7.4,a,f7.4,a,f7.4)', &
      i, ',', trim(names(i)), ',', confidence(i), ',', bias_risk(i), ',', ai_risk(i), ',', readiness(i), ',', governance_priority(i)
  end do

contains

  subroutine sort_desc(names, confidence, bias, ai, readiness, priority, n)
    integer, intent(in) :: n
    character(len=160), intent(inout) :: names(n)
    real(8), intent(inout) :: confidence(n), bias(n), ai(n), readiness(n), priority(n)
    integer :: i, j
    real(8) :: tc, tb, ta, tr, tp
    character(len=160) :: tn

    do i = 1, n - 1
      do j = i + 1, n
        if (priority(j) > priority(i)) then
          tp = priority(i); priority(i) = priority(j); priority(j) = tp
          tc = confidence(i); confidence(i) = confidence(j); confidence(j) = tc
          tb = bias(i); bias(i) = bias(j); bias(j) = tb
          ta = ai(i); ai(i) = ai(j); ai(j) = ta
          tr = readiness(i); readiness(i) = readiness(j); readiness(j) = tr
          tn = names(i); names(i) = names(j); names(j) = tn
        end if
      end do
    end do
  end subroutine sort_desc

end program research_signal_model
