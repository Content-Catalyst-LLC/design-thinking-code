program strategy_option_model
  implicit none

  integer, parameter :: n = 8
  character(len=160) :: names(n)
  real(8) :: desirability(n), feasibility(n), viability(n), alignment(n), ethics(n)
  real(8) :: learning(n), effort(n), risk(n), capability_gap(n), evidence(n)
  real(8) :: time_to_learn(n), public_value(n), score(n), portfolio(n)
  integer :: i

  names = [ character(len=160) :: &
    "Simplify Core Service Journey", &
    "Launch Assisted Access Model", &
    "Build AI-Supported Research Synthesis", &
    "Create Community Partnership Channel", &
    "Redesign Onboarding and Adoption System", &
    "Develop Strategic Learning Dashboard", &
    "Prototype Public Value Governance Review", &
    "Build Frontline Implementation Lab" ]

  desirability = [8.6d0, 8.8d0, 7.4d0, 8.2d0, 8.0d0, 7.6d0, 7.8d0, 8.4d0]
  feasibility = [7.4d0, 6.8d0, 6.6d0, 6.2d0, 7.2d0, 7.0d0, 6.4d0, 6.6d0]
  viability = [7.8d0, 7.0d0, 7.2d0, 6.8d0, 7.4d0, 7.0d0, 6.6d0, 7.0d0]
  alignment = [8.8d0, 8.4d0, 7.8d0, 8.0d0, 8.2d0, 8.6d0, 8.0d0, 8.4d0]
  ethics = [8.2d0, 9.0d0, 6.8d0, 8.6d0, 7.8d0, 7.6d0, 9.2d0, 8.4d0]
  learning = [7.4d0, 8.2d0, 8.8d0, 8.0d0, 7.6d0, 8.6d0, 8.4d0, 8.6d0]
  effort = [6.2d0, 7.0d0, 7.6d0, 6.8d0, 6.4d0, 7.2d0, 6.6d0, 7.4d0]
  risk = [4.2d0, 4.6d0, 6.8d0, 5.4d0, 4.8d0, 5.8d0, 5.2d0, 5.6d0]
  capability_gap = [4.8d0, 5.8d0, 6.8d0, 6.4d0, 5.2d0, 6.0d0, 5.6d0, 6.2d0]
  evidence = [0.72d0, 0.66d0, 0.54d0, 0.60d0, 0.70d0, 0.62d0, 0.58d0, 0.64d0]
  time_to_learn = [4.0d0, 5.0d0, 4.5d0, 6.0d0, 3.5d0, 4.0d0, 5.0d0, 5.5d0]
  public_value = [8.0d0, 9.2d0, 7.0d0, 9.0d0, 7.6d0, 7.4d0, 9.4d0, 8.8d0]

  do i = 1, n
    score(i) = 0.17d0 * desirability(i) + &
               0.13d0 * feasibility(i) + &
               0.13d0 * viability(i) + &
               0.16d0 * alignment(i) + &
               0.11d0 * ethics(i) + &
               0.10d0 * learning(i) + &
               0.08d0 * public_value(i) + &
               0.05d0 * evidence(i) * 10.0d0 - &
               0.03d0 * risk(i) - &
               0.02d0 * effort(i) - &
               0.01d0 * capability_gap(i) - &
               0.01d0 * time_to_learn(i)

    portfolio(i) = score(i) + &
                   0.30d0 * learning(i) + &
                   0.20d0 * public_value(i) + &
                   0.15d0 * evidence(i) * 10.0d0 - &
                   0.22d0 * risk(i) - &
                   0.14d0 * effort(i) - &
                   0.10d0 * capability_gap(i)
  end do

  call sort_desc(names, score, portfolio, risk, n)

  print '(a)', 'rank,option,strategic_score,portfolio_value,strategic_risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', score(i), ',', portfolio(i), ',', risk(i)
  end do

contains

  subroutine sort_desc(names, score, portfolio, risk, n)
    integer, intent(in) :: n
    character(len=160), intent(inout) :: names(n)
    real(8), intent(inout) :: score(n), portfolio(n), risk(n)
    integer :: i, j
    real(8) :: temp_score, temp_portfolio, temp_risk
    character(len=160) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (score(j) > score(i)) then
          temp_score = score(i)
          score(i) = score(j)
          score(j) = temp_score

          temp_portfolio = portfolio(i)
          portfolio(i) = portfolio(j)
          portfolio(j) = temp_portfolio

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

end program strategy_option_model
