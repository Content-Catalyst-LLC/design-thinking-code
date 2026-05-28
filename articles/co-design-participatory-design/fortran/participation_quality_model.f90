program participation_quality_model
  implicit none

  integer, parameter :: n = 10
  character(len=128) :: names(n)
  real(8) :: representation(n), accessibility(n), participant_influence(n)
  real(8) :: trust_quality(n), evidence_quality(n), implementation_accountability(n)
  real(8) :: decision_impact(n), ethical_risk(n), quality(n)
  integer :: i

  names = [ character(len=128) :: &
    "Community Problem-Framing Sessions", &
    "Frontline Worker Journey Mapping", &
    "Non-User Contextual Inquiry", &
    "Accessible Prototype Workshops", &
    "Participatory Synthesis Review", &
    "AI Decision-Scenario Walkthroughs", &
    "Implementation Governance Board", &
    "Community Feedback and Accountability Forum", &
    "Caregiver Service Blueprinting", &
    "Participatory Data Rights Review" ]

  representation = [7.8d0, 8.0d0, 6.4d0, 7.2d0, 6.8d0, 6.0d0, 7.0d0, 7.6d0, 7.4d0, 6.8d0]
  accessibility = [7.4d0, 7.8d0, 6.2d0, 8.4d0, 7.0d0, 6.6d0, 7.2d0, 8.0d0, 7.2d0, 6.8d0]
  participant_influence = [7.6d0, 7.2d0, 6.8d0, 7.8d0, 7.0d0, 6.4d0, 8.0d0, 7.4d0, 7.0d0, 7.2d0]
  trust_quality = [7.0d0, 7.4d0, 5.8d0, 7.2d0, 6.8d0, 6.2d0, 7.0d0, 7.8d0, 6.9d0, 6.6d0]
  evidence_quality = [7.2d0, 8.0d0, 6.6d0, 7.4d0, 7.0d0, 6.5d0, 7.2d0, 7.4d0, 7.5d0, 7.1d0]
  implementation_accountability = [6.8d0, 6.6d0, 5.8d0, 6.4d0, 7.0d0, 7.2d0, 8.4d0, 8.0d0, 6.7d0, 7.8d0]
  decision_impact = [7.4d0, 7.0d0, 6.2d0, 6.8d0, 7.2d0, 6.6d0, 8.2d0, 7.8d0, 6.9d0, 7.4d0]
  ethical_risk = [3.8d0, 3.4d0, 5.2d0, 4.0d0, 3.6d0, 6.4d0, 4.2d0, 3.5d0, 4.1d0, 5.6d0]

  do i = 1, n
    quality(i) = 0.18d0 * representation(i) + &
                 0.14d0 * accessibility(i) + &
                 0.22d0 * participant_influence(i) + &
                 0.12d0 * trust_quality(i) + &
                 0.12d0 * evidence_quality(i) + &
                 0.12d0 * implementation_accountability(i) + &
                 0.14d0 * decision_impact(i) - &
                 0.08d0 * ethical_risk(i)
  end do

  call sort_desc(names, quality, ethical_risk, n)

  print '(a)', 'rank,activity,participation_quality,ethical_risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', quality(i), ',', ethical_risk(i)
  end do

contains

  subroutine sort_desc(names, values, risks, n)
    integer, intent(in) :: n
    character(len=128), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n), risks(n)
    integer :: i, j
    real(8) :: temp_value, temp_risk
    character(len=128) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_risk = risks(i)
          risks(i) = risks(j)
          risks(j) = temp_risk

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program participation_quality_model
