module input_namelists

    integer :: eb = 8
    integer :: mxpts = 200
    integer :: mxtablcols = 25
    integer :: default_grid = 50

    implicit none

    ! &HEAD Namelist
    integer :: version = 0
    character(len=256) :: title = ' '
    namelist /HEAD/ version, title

    ! &TIME Namelist
    real(eb) :: print = 60.0_eb
    real(eb) :: simulation = 900.0_eb
    real(eb) :: spreadsheet = 15.0_eb
    real(eb) :: smokeview = 15.0_eb
    namelist /TIME/ print, simulation, spreadsheet, smokeview

    ! &INIT Namelist
    real(eb) :: pressure = 101325.0_eb
    real(eb) :: relative_humidity = 50.0_eb
    real(eb) :: interior_temperature = 20.0_eb
    real(eb) :: exterior_temperature = 20.0_eb
    real(eb) :: interior_o2_mass_fraction = 0.23_eb
    real(eb) :: exterior_o2_mass_fraction = 0.23_eb
    namelist /INIT/ pressure, relative_humidity, interior_temperature, exterior_temperature, &
                    interior_o2_mass_fraction, exterior_o2_mass_fraction

    ! &MISC Namelist
    logical :: adiabatic = .false.
    real(eb) :: max_time_step = 1.0_eb
    real(eb) :: max_iteration = -1.0_eb
    real(eb) :: lower_oxygen_limit = 0.15_eb
    real(eb), dimension(2) :: specific_extinction = (/8700.0_eb, 4400.0_eb/)
    logical :: overwrite = .true.
    namelist /MISC/ adiabatic, max_time_step, max_iteration, lower_oxygen_limit, specific_extinction, overwrite

    ! &MATL Namelist
    real(eb) :: conductivity = 0.0_eb
    real(eb) :: density = 0.0_eb
    real(eb) :: emissivity = 0.9_eb
    character(len=64) :: id = 'NULL'
    character(len=64) :: material = 'NULL'
    real(eb) :: specific_heat = 0.0_eb
    real(eb) :: thickness = 0.0_eb
    character(len=128) :: fyi = ' '
    namelist /MATL/ conductivity, density, emissivity, id, material, specific_heat, thickness, fyi

    ! &COMP Namelist
    real(eb), dimension(mxpts) :: cross_sect_areas = -1001.0_eb
    real(eb), dimension(mxpts) :: cross_sect_heights = -1001.0_eb
    real(eb) :: depth = 0.0_eb
    integer, dimension(3) :: grid = 50
    logical :: hall = .false.
    real(eb) :: height = 0.0_eb
    character(len=64) :: comp_id = 'NULL'
    character(len=64), dimension(3) :: ceiling_matl_id = 'OFF'
    character(len=64), dimension(3) :: floor_matl_id = 'OFF'
    character(len=64), dimension(3) :: wall_matl_id = 'OFF'
    real(eb), dimension(3) :: ceiling_thickness = 0.0_eb
    real(eb), dimension(3) :: floor_thickness = 0.0_eb
    real(eb), dimension(3) :: wall_thickness = 0.0_eb
    real(eb), dimension(3) :: origin = 0.0_eb
    logical :: shaft = .false.
    real(eb) :: width = 0.0_eb
    real(eb), dimension(2) :: leak_area_ratio = 0.0_eb
    real(eb), dimension(2) :: leak_area = 0.0_eb
    real(eb) :: flow_coefficient = 0.07_eb
    namelist /COMP/ cross_sect_areas, cross_sect_heights, depth, grid, hall, height, id, fyi, &
                    ceiling_matl_id, floor_matl_id, wall_matl_id, ceiling_thickness, floor_thickness, &
                    wall_thickness, origin, shaft, width, leak_area_ratio, leak_area, flow_coefficient

    ! &DEVC Namelist
    character(len=64) :: type = 'NULL'
    real(eb) :: temperature_depth = 0.5_eb
    character(len=64) :: depth_units = 'FRACTION'
    real(eb), dimension(3) :: location = (/-1.0_eb, -1.0_eb, -0.0762_eb/)
    character(len=64) :: matl_id = 'NULL'
    real(eb), dimension(3) :: normal = (/0.0_eb, 0.0_eb, 1.0_eb/)
    character(len=64) :: surface_orientation = 'NULL'
    real(eb) :: surface_temperature = 20.0_eb
    real(eb) :: rti = 50.0_eb
    real(eb) :: setpoint = -1001.0_eb
    real(eb) :: spray_density = -300.0_eb
    real(eb), dimension(2) :: setpoints = -1001.0_eb
    logical :: adiabatic_target = .false.
    real(eb), dimension(2) :: convection_coefficients = 0.0_eb
    namelist /DEVC/ comp_id, type, id, temperature_depth, depth_units, location, matl_id, normal, &
                    surface_orientation, surface_temperature, thickness, rti, setpoint, spray_density, &
                    setpoints, adiabatic_target, convection_coefficients, fyi

    ! &RAMP Namelist
    real(eb), dimension(mxpts) :: f = -1001.0_eb
    real(eb), dimension(mxpts) :: t = -1001.0_eb
    real(eb), dimension(mxpts) :: z = -1001.0_eb
    character(len=64), dimension(2) :: comp_ids = 'NULL'
    namelist /RAMP/ f, id, t, z, type, comp_ids

    ! &TABL Namelist
    character(len=64), dimension(mxtablcols) :: labels = 'NULL'
    real(eb), dimension(mxtablcols) :: data = -1001.0_eb
    namelist /TABL/ id, labels, data

    ! &FIRE Namelist
    character(len=64) :: devc_id = 'NULL'
    character(len=64) :: fire_id = 'NULL'
    character(len=64) :: ignition_criterion = 'TIME'
    real(eb), dimension(2) :: fire_location = 0.0_eb
    namelist /FIRE/ comp_id, devc_id, fire_id, id, ignition_criterion, location, setpoint, fyi

    ! &CHEM Namelist
    real(eb) :: area = 0.0_eb
    real(eb) :: carbon = 0.0_eb
    real(eb) :: chlorine = 0.0_eb
    real(eb) :: co_yield = 0.0_eb
    real(eb) :: heat_of_combustion = 50000.0_eb
    real(eb) :: hcn_yield = 0.0_eb
    real(eb) :: hrr = 0.0_eb
    real(eb) :: hydrogen = 0.0_eb
    real(eb) :: nitrogen = 0.0_eb
    real(eb) :: oxygen = 0.0_eb
    real(eb) :: radiative_fraction = 0.0_eb
    real(eb) :: soot_yield = 0.0_eb
    character(len=64) :: table_id = 'NULL'
    real(eb) :: trace_yield = 0.0_eb
    real(eb) :: flaming_transition_time = 0.0_eb
    namelist /CHEM/ area, carbon, chlorine, comp_id, co_yield, heat_of_combustion, &
                    hcn_yield, hrr, hydrogen, id, nitrogen, oxygen, radiative_fraction, &
                    soot_yield, table_id, trace_yield, flaming_transition_time

    ! &VENT Namelist
    real(eb), dimension(2) :: areas = 0.0_eb
    real(eb) :: bottom = 0.0_eb
    character(len=64) :: criterion = 'TIME'
    real(eb), dimension(2) :: cutoffs = (/200.0_eb, 300.0_eb/)
    character(len=64) :: face = 'NULL'
    real(eb) :: filter_efficiency = 0.0_eb
    real(eb) :: filter_time = 0.0_eb
    real(eb) :: flow = 0.0_eb
    real(eb), dimension(2) :: heights = 0.0_eb
    real(eb) :: offset = 0.0_eb
    real(eb), dimension(2) :: offsets = 0.0_eb
    character(len=64), dimension(2) :: orientations = 'VERTICAL'
    real(eb) :: pre_fraction = 1.0_eb
    real(eb) :: post_fraction = 1.0_eb
    character(len=64) :: shape = 'NULL'
    real(eb) :: top = 0.0_eb
    namelist /VENT/ area, areas, bottom, comp_ids, criterion, cutoffs, devc_id, f, face, &
                    filter_efficiency, filter_time, flow, height, heights, id, offset, offsets, &
                    orientations, pre_fraction, post_fraction, setpoint, shape, t, top, type, &
                    width, fyi, flow_coefficient

    ! &CONN Namelist
    namelist /CONN/ comp_id, comp_ids, f, type

    ! &ISOF Namelist
    real(eb) :: value = -1001.0_eb
    namelist /ISOF/ comp_id, value

    ! &SLCF Namelist
    character(len=64) :: domain = 'NULL'
    character(len=64) :: plane = 'NULL'
    real(eb) :: position = 0.0_eb
    namelist /SLCF/ domain, plane, position, comp_id

    ! &DIAG Namelist
    character(len=8) :: mode = ' '
    character(len=64) :: rad_solver = 'NULL'
    real(eb) :: partial_pressure_h2o = -1001.0_eb
    real(eb) :: partial_pressure_co2 = -1001.0_eb
    real(eb) :: gas_temperature = -1001.0_eb
    character(len=3) :: horizontal_flow_sub_model = 'ON'
    character(len=3) :: fire_sub_model = 'ON'
    character(len=3) :: entrainment_sub_model = 'ON'
    character(len=3) :: vertical_flow_sub_model = 'ON'
    character(len=3) :: ceiling_jet_sub_model = 'ON'
    character(len=3) :: door_jet_fire_sub_model = 'ON'
    character(len=3) :: convection_sub_model = 'ON'
    character(len=3) :: radiation_sub_model = 'ON'
    character(len=3) :: conduction_sub_model = 'ON'
    character(len=3) :: debug_print = 'OFF'
    character(len=3) :: mechanical_flow_sub_model = 'ON'
    character(len=3) :: keyboard_input = 'ON'
    character(len=3) :: steady_state_initial_conditions = 'OFF'
    character(len=3) :: dassl_debug_print = 'OFF'
    character(len=3) :: oxygen_tracking = 'OFF'
    character(len=10) :: gas_absorbtion_sub_model = 'CALCULATED'
    character(len=3) :: residual_debug_print = 'OFF'
    character(len=3) :: layer_mixing_sub_model = 'ON'
    character(len=3) :: adiabatic_target_verification = 'OFF'
    real(eb) :: radiative_incident_flux = 0.0_eb
    real(eb) :: upper_layer_thickness = -1001.0_eb
    real(eb) :: verification_time_step = 0.0_eb
    real(eb) :: verification_fire_heat_flux = -1001.0_eb
    namelist /DIAG/ mode, rad_solver, partial_pressure_h2o, partial_pressure_co2, gas_temperature, t, f, &
                    horizontal_flow_sub_model, fire_sub_model, entrainment_sub_model, vertical_flow_sub_model, &
                    ceiling_jet_sub_model, door_jet_fire_sub_model, convection_sub_model, radiation_sub_model, &
                    conduction_sub_model, debug_print, mechanical_flow_sub_model, keyboard_input, &
                    steady_state_initial_conditions, dassl_debug_print, oxygen_tracking, &
                    gas_absorbtion_sub_model, residual_debug_print, layer_mixing_sub_model, &
                    adiabatic_target_verification, radiative_incident_flux, upper_layer_thickness, &
                    verification_time_step, verification_fire_heat_flux

    ! &DUMP Namelist
    character(len=25) :: file = ' '
    character(len=64) :: first_device = ' '
    character(len=64) :: first_measurement = ' '
    character(len=64) :: second_device = ' '
    character(len=64) :: second_measurement = ' '
    character(len=64), dimension(2) :: first_field = ' '
    character(len=64), dimension(2) :: second_field = ' '
    real(eb) :: dump_criterion = 0.0_eb
    namelist /DUMP/ id, file, first_device, first_measurement, second_device, &
                    second_measurement, first_field, second_field, criterion, type, fyi

end module input_namelists
