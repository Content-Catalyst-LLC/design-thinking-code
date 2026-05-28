program ethical_risk_model
  implicit none

  integer, parameter :: n = 8
  character(len=160) :: names(n)
  real(8) :: harm(n), probability(n), exposure(n), detectability(n), accountability(n)
  real(8) :: inclusion(n), public_value(n), repairability(n), privacy(n), autonomy(n), manipulation(n)
  real(8) :: ethical_risk(n), review_priority(n)
  integer :: i

  names = [ character(len=160) :: &
    "Digital-first access", &
    "AI-assisted case prioritization", &
    "Behavioral reminder campaign", &
    "Reduced human support", &
    "Community co-design process", &
    "Data-driven personalization", &
    "Automated eligibility triage", &
    "Plain-language redesign" ]

  harm = [0.72d0, 0.86d0, 0.42d0, 0.76d0, 0.28d0, 0.70d0, 0.90d0, 0.22d0]
  probability = [0.54d0, 0.48d0, 0.40d0, 0.58d0, 0.30d0, 0.46d0, 0.42d0, 0.24d0]
  exposure = [0.80d0, 0.62d0, 0.74d0, 0.68d0, 0.42d0, 0.66d0, 0.56d0, 0.70d0]
  detectability = [0.46d0, 0.38d0, 0.66d0, 0.42d0, 0.72d0, 0.44d0, 0.34d0, 0.78d0]
  accountability = [0.42d0, 0.36d0, 0.58d0, 0.40d0, 0.76d0, 0.38d0, 0.32d0, 0.72d0]
  inclusion = [0.52d0, 0.46d0, 0.62d0, 0.44d0, 0.78d0, 0.48d0, 0.40d0, 0.74d0]
  public_value = [0.70d0, 0.74d0, 0.64d0, 0.62d0, 0.88d0, 0.68d0, 0.80d0, 0.76d0]
  repairability = [0.46d0, 0.36d0, 0.58d0, 0.34d0, 0.74d0, 0.44d0, 0.30d0, 0.78d0]
  privacy = [0.44d0, 0.82d0, 0.50d0, 0.38d0, 0.32d0, 0.84d0, 0.78d0, 0.26d0]
  autonomy = [0.48d0, 0.62d0, 0.54d0, 0.46d0, 0.22d0, 0.68d0, 0.72d0, 0.18d0]
  manipulation = [0.30d0, 0.44d0, 0.66d0, 0.28d0, 0.18d0, 0.58d0, 0.48d0, 0.16d0]

  do i = 1, n
    ethical_risk(i) = harm(i) * probability(i) * exposure(i) * (1.0d0 - detectability(i)) * (1.0d0 - accountability(i))

    review_priority(i) = 0.32d0 * ethical_risk(i) + &
                         0.20d0 * harm(i) + &
                         0.14d0 * exposure(i) + &
                         0.10d0 * (1.0d0 - accountability(i)) + &
                         0.08d0 * (1.0d0 - detectability(i)) + &
                         0.06d0 * (1.0d0 - inclusion(i)) + &
                         0.05d0 * privacy(i) + &
                         0.03d0 * autonomy(i) + &
                         0.02d0 * manipulation(i) - &
                         0.12d0 * public_value(i) + &
                         0.10d0 * (1.0d0 - repairability(i))
  end do

  call sort_desc(names, ethical_risk, review_priority, n)

  print '(a)', 'rank,design_decision,ethical_risk,review_priority'
  do i = 1, n
    print '(i0,a,a,a,f8.5,a,f8.5)', i, ',', trim(names(i)), ',', ethical_risk(i), ',', review_priority(i)
  end do

contains

  subroutine sort_desc(names, risk, priority, n)
    integer, intent(in) :: n
    character(len=160), intent(inout) :: names(n)
    real(8), intent(inout) :: risk(n), priority(n)
    integer :: i, j
    real(8) :: temp_risk, temp_priority
    character(len=160) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (priority(j) > priority(i)) then
          temp_priority = priority(i)
          priority(i) = priority(j)
          priority(j) = temp_priority

          temp_risk = risk(i)
          risk(i) = risk(j)
          risk(j) = temp_risk

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program ethical_risk_model
