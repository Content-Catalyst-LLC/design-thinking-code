program validation_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: desirability(n), feasibility(n), viability(n), responsibility(n)
  real(8) :: friction(n), residual_risk(n), combined_risk(n), values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Guided Onboarding Flow", &
    "Simplified Intake Form", &
    "Service Navigation Wizard", &
    "Follow-Up Reminder System", &
    "Human Support Escalation Pathway", &
    "Status Visibility Dashboard", &
    "Exception Handling Service Blueprint", &
    "Plain-Language Eligibility Guide" ]

  desirability = [8.5d0, 8.0d0, 7.9d0, 7.6d0, 8.4d0, 8.2d0, 8.1d0, 8.3d0]
  feasibility = [7.6d0, 8.4d0, 7.3d0, 8.1d0, 7.2d0, 7.8d0, 7.5d0, 8.6d0]
  viability = [7.8d0, 8.0d0, 7.5d0, 8.2d0, 7.4d0, 7.7d0, 7.6d0, 8.1d0]
  responsibility = [7.6d0, 8.2d0, 7.3d0, 7.8d0, 8.5d0, 7.9d0, 8.3d0, 8.4d0]
  friction = [3.9d0, 3.4d0, 4.5d0, 3.7d0, 4.1d0, 3.8d0, 4.0d0, 3.2d0]
  residual_risk = [4.0d0, 3.5d0, 4.6d0, 3.9d0, 4.3d0, 4.1d0, 4.2d0, 3.3d0]

  do i = 1, n
    combined_risk(i) = 0.50d0 * friction(i) + 0.50d0 * residual_risk(i)
    values(i) = 0.25d0 * desirability(i) + &
                0.20d0 * feasibility(i) + &
                0.20d0 * viability(i) + &
                0.20d0 * responsibility(i) - &
                0.15d0 * combined_risk(i)
  end do

  call sort_desc(names, values, combined_risk, n)

  print '(a)', 'rank,concept,validation_value,combined_risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', values(i), ',', combined_risk(i)
  end do

contains

  subroutine sort_desc(names, values, risks, n)
    integer, intent(in) :: n
    character(len=96), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n), risks(n)
    integer :: i, j
    real(8) :: temp_value, temp_risk
    character(len=96) :: temp_name

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

end program validation_value_model
