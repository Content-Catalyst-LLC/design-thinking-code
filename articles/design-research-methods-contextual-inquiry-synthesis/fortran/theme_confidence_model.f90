program theme_confidence_model
  implicit none

  integer, parameter :: n = 7
  character(len=64) :: themes(n)
  real(8) :: evidence_strength(n), stakeholder_coverage(n), method_triangulation(n), interpretive_risk(n)
  real(8) :: confidence(n)
  integer :: i

  themes = [ character(len=64) :: &
    "status_uncertainty", &
    "documentation_confusion", &
    "translation_labor", &
    "manual_workaround", &
    "policy_complexity", &
    "trust_gap", &
    "access_barrier" ]

  evidence_strength    = [8.2d0, 7.6d0, 8.2d0, 8.35d0, 7.3d0, 7.9d0, 8.54d0]
  stakeholder_coverage = [7.5d0, 8.0d0, 8.0d0, 7.0d0, 7.5d0, 8.0d0, 9.0d0]
  method_triangulation = [8.0d0, 8.0d0, 7.5d0, 8.5d0, 7.0d0, 7.5d0, 8.5d0]
  interpretive_risk    = [3.55d0, 3.98d0, 3.95d0, 3.60d0, 4.22d0, 4.05d0, 4.50d0]

  do i = 1, n
    confidence(i) = 0.35d0 * evidence_strength(i) + &
                    0.25d0 * stakeholder_coverage(i) + &
                    0.25d0 * method_triangulation(i) - &
                    0.15d0 * interpretive_risk(i)
  end do

  call sort_desc(themes, confidence, n)

  print '(a)', 'rank,theme,synthesis_confidence'
  do i = 1, n
    print '(i0,a,a,a,f8.4)', i, ',', trim(themes(i)), ',', confidence(i)
  end do

contains

  subroutine sort_desc(themes, values, n)
    integer, intent(in) :: n
    character(len=64), intent(inout) :: themes(n)
    real(8), intent(inout) :: values(n)
    integer :: i, j
    real(8) :: temp_value
    character(len=64) :: temp_theme

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_theme = themes(i)
          themes(i) = themes(j)
          themes(j) = temp_theme
        end if
      end do
    end do
  end subroutine sort_desc

end program theme_confidence_model
