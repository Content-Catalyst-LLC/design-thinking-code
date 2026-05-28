program human_centered_value_model
  implicit none

  integer, parameter :: n = 7
  character(len=64) :: names(n)
  real(8) :: human_benefit(n), usability(n), stakeholder_fit(n), burden(n)
  real(8) :: values(n)
  integer :: i

  names = [ character(len=64) :: &
    "Guided Intake Redesign", &
    "Simplified Mobile Access Flow", &
    "Community Support Navigator", &
    "AI Self-Service Assistant", &
    "Hybrid Human-Digital Support Model", &
    "In-Person Assisted Enrollment", &
    "Plain-Language Eligibility Redesign" ]

  human_benefit  = [8.7d0, 8.0d0, 8.9d0, 7.4d0, 8.6d0, 8.8d0, 8.4d0]
  usability      = [8.2d0, 8.8d0, 7.6d0, 8.1d0, 8.4d0, 7.3d0, 8.6d0]
  stakeholder_fit= [8.1d0, 7.7d0, 8.6d0, 6.9d0, 8.3d0, 8.7d0, 8.2d0]
  burden         = [3.9d0, 3.5d0, 4.2d0, 5.0d0, 3.7d0, 4.6d0, 3.2d0]

  do i = 1, n
    values(i) = 0.30d0 * human_benefit(i) + &
                0.25d0 * usability(i) + &
                0.30d0 * stakeholder_fit(i) - &
                0.15d0 * burden(i)
  end do

  call sort_desc(names, values, n)

  print '(a)', 'rank,option,hc_value'
  do i = 1, n
    print '(i0,a,a,a,f8.4)', i, ',', trim(names(i)), ',', values(i)
  end do

contains

  subroutine sort_desc(names, values, n)
    integer, intent(in) :: n
    character(len=64), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n)
    integer :: i, j
    real(8) :: temp_value
    character(len=64) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program human_centered_value_model
