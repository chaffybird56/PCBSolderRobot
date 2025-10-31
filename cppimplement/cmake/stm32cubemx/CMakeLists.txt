cmake_minimum_required(VERSION 3.22)

project(stm32cubemx)
add_library(stm32cubemx INTERFACE)

# Enable CMake support for ASM and C languages
enable_language(C ASM)

target_compile_definitions(stm32cubemx INTERFACE 
	USE_NUCLEO_64 
	USE_HAL_DRIVER 
	STM32H503xx
    $<$<CONFIG:Debug>:DEBUG>
)

target_include_directories(stm32cubemx INTERFACE
    ../../Core/Inc
    ../../Drivers/STM32H5xx_HAL_Driver/Inc
    ../../Drivers/STM32H5xx_HAL_Driver/Inc/Legacy
    ../../Drivers/BSP/STM32H5xx_Nucleo
    ../../Drivers/CMSIS/Device/ST/STM32H5xx/Include
    ../../Drivers/CMSIS/Include
)

target_sources(stm32cubemx INTERFACE
    ../../Core/Src/main.cpp
    ../../Core/Src/stm32h5xx_it.c
    ../../Core/Src/stm32h5xx_hal_msp.c
    ../../Drivers/BSP/STM32H5xx_Nucleo/stm32h5xx_nucleo.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_cortex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_icache.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_rcc.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_rcc_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_flash.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_flash_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_gpio.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_dma.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_dma_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_pwr.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_pwr_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_exti.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_tim.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_tim_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_usart.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_usart_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_uart_ex.c
    ../../Drivers/STM32H5xx_HAL_Driver/Src/stm32h5xx_hal_uart.c
    ../../Core/Src/system_stm32h5xx.c
    ../../Core/Src/sysmem.c
    ../../Core/Src/syscalls.c
    ../../startup_stm32h503xx.s
)

target_link_directories(stm32cubemx INTERFACE
)

target_link_libraries(stm32cubemx INTERFACE
)

# Validate that STM32CubeMX code is compatible with C standard
if(CMAKE_C_STANDARD LESS 11)
    message(ERROR "Generated code requires C11 or higher")
endif()


