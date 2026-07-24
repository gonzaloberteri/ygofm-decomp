SECTIONS
{
    HIDDEN(__romPos = 0);
    main_ROM_START = __romPos;
    main_VRAM = ADDR(.main);
    .main 0x80010000 : AT(main_ROM_START) SUBALIGN(16)
    {
        FILL(0x00000000);
        main_TEXT_START = .;
        build/asm/code_002800.s.o(.text);
        . = ALIGN(., 16);
        main_TEXT_END = .;
        main_TEXT_SIZE = ABSOLUTE(main_TEXT_END - main_TEXT_START);
        main_DATA_START = .;
        build/assets/data_000000.bin.o(.data);
        build/asm/code_002800.s.o(.data);
        build/assets/data_082C00.bin.o(.data);
        build/assets/zero_08B400.bin.o(.data);
        build/assets/data_12A000.bin.o(.data);
        build/assets/zero_12A400.bin.o(.data);
        build/assets/data_12B000.bin.o(.data);
        build/assets/zero_12B400.bin.o(.data);
        build/assets/data_136000.bin.o(.data);
        build/assets/zero_136400.bin.o(.data);
        build/assets/data_158000.bin.o(.data);
        build/assets/zero_158400.bin.o(.data);
        build/assets/data_16A000.bin.o(.data);
        build/assets/zero_16A400.bin.o(.data);
        build/assets/data_16B000.bin.o(.data);
        build/assets/zero_16B400.bin.o(.data);
        build/assets/data_170000.bin.o(.data);
        build/assets/zero_170400.bin.o(.data);
        build/assets/data_19C000.bin.o(.data);
        build/assets/zero_19DC00.bin.o(.data);
        build/assets/data_1A0000.bin.o(.data);
        build/assets/zero_1AFC00.bin.o(.data);
        build/assets/data_1B0000.bin.o(.data);
        build/assets/zero_1BD800.bin.o(.data);
        build/assets/data_1C4000.bin.o(.data);
        build/assets/zero_1C9400.bin.o(.data);
        . = ALIGN(., 16);
        main_DATA_END = .;
        main_DATA_SIZE = ABSOLUTE(main_DATA_END - main_DATA_START);
        main_RODATA_START = .;
        build/asm/code_002800.s.o(.rodata);
        . = ALIGN(., 16);
        main_RODATA_END = .;
        main_RODATA_SIZE = ABSOLUTE(main_RODATA_END - main_RODATA_START);
        main_BSS_START = .;
        build/asm/code_002800.s.o(.bss);
        . = ALIGN(., 16);
        main_BSS_END = .;
        main_BSS_SIZE = ABSOLUTE(main_BSS_END - main_BSS_START);
    }
    __romPos += SIZEOF(.main);
    __romPos = ALIGN(__romPos, 16);
    . = ALIGN(., 16);
    main_ROM_END = __romPos;
    main_VRAM_END = .;

    /DISCARD/ :
    {
        *(*);
    }
}
