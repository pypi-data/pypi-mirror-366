/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2013-2023 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
#ifndef MICROPY_INCLUDED_PY_NLR_H
#define MICROPY_INCLUDED_PY_NLR_H

// non-local return
// exception handling, basically a stack of setjmp/longjmp buffers

#include <limits.h>
#include <assert.h>
#include <stdbool.h>

#include "py/mpconfig.h"

#define MICROPY_NLR_NUM_REGS_X86            (6)
#define MICROPY_NLR_NUM_REGS_X64            (8)
#define MICROPY_NLR_NUM_REGS_X64_WIN        (10)
#define MICROPY_NLR_NUM_REGS_ARM_THUMB      (10)
#define MICROPY_NLR_NUM_REGS_ARM_THUMB_FP   (10 + 6)
#define MICROPY_NLR_NUM_REGS_AARCH64        (13)
#define MICROPY_NLR_NUM_REGS_MIPS           (13)
#define MICROPY_NLR_NUM_REGS_XTENSA         (10)
#define MICROPY_NLR_NUM_REGS_XTENSAWIN      (17)
#define MICROPY_NLR_NUM_REGS_RV32I          (14)
#define MICROPY_NLR_NUM_REGS_RV64I          (14)

// *FORMAT-OFF*

// If MICROPY_NLR_SETJMP is not enabled then auto-detect the machine arch
#if !MICROPY_NLR_SETJMP && !MICROPY_NLR_WASM
// A lot of nlr-related things need different treatment on Windows
#if defined(_WIN32) || defined(__CYGWIN__)
#define MICROPY_NLR_OS_WINDOWS 1
#else
#define MICROPY_NLR_OS_WINDOWS 0
#endif
#if defined(__i386__)
    #define MICROPY_NLR_X86 (1)
    #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_X86)
#elif defined(__x86_64__)
    #define MICROPY_NLR_X64 (1)
    #if MICROPY_NLR_OS_WINDOWS
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_X64_WIN)
    #else
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_X64)
    #endif
#elif defined(__thumb2__) || defined(__thumb__) || defined(__arm__)
    #define MICROPY_NLR_THUMB (1)
    #if defined(__SOFTFP__)
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_ARM_THUMB)
    #else
        // With hardware FP registers s16-s31 are callee save so in principle
        // should be saved and restored by the NLR code.  gcc only uses s16-s21
        // so only save/restore those as an optimisation.
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_ARM_THUMB_FP)
    #endif
#elif defined(__aarch64__)
    #define MICROPY_NLR_AARCH64 (1)
    #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_AARCH64)
#elif defined(__xtensa__)
    #define MICROPY_NLR_XTENSA (1)
    #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_XTENSA)
#elif defined(__powerpc__)
    #define MICROPY_NLR_POWERPC (1)
    // this could be less but using 128 for safety
    #define MICROPY_NLR_NUM_REGS (128)
#elif defined(__mips__)
    #define MICROPY_NLR_MIPS (1)
    #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_MIPS)
#elif defined(__riscv)
    #if __riscv_xlen == 32
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_RV32I)
        #define MICROPY_NLR_RV32I (1)
    #elif __riscv_xlen == 64
        #define MICROPY_NLR_NUM_REGS (MICROPY_NLR_NUM_REGS_RV64I)
        #define MICROPY_NLR_RV64I (1)
    #else
        #error Unsupported RISC-V variant.
    #endif
#else
    // #define MICROPY_NLR_SETJMP (1)
    #define MICROPY_NLR_WASM (1)
    //#warning "No native NLR support for this arch, using setjmp implementation"
#endif
#endif

#if MICROPY_NLR_WASM
    #define MICROPY_NLR_NUM_REGS (1)
#endif

// *FORMAT-ON*

#if MICROPY_NLR_SETJMP
#include <setjmp.h>
#endif

typedef struct _nlr_buf_t nlr_buf_t;
struct _nlr_buf_t {
    // The entries in this struct must all be machine word size.

    // Pointer to the previous nlr_buf_t in the chain.
    // Or NULL if it's the top-level one.
    nlr_buf_t *prev;

    // The exception that is being raised:
    // - NULL means the jump is because of a VM abort (only if MICROPY_ENABLE_VM_ABORT enabled)
    // - otherwise it's always a concrete object (an exception instance)
    void *ret_val;

    #if MICROPY_NLR_SETJMP
    jmp_buf jmpbuf;
    #else
    void *regs[MICROPY_NLR_NUM_REGS];
    #endif

    #if MICROPY_ENABLE_PYSTACK
    void *pystack;
    #endif
};

typedef void (*nlr_jump_callback_fun_t)(void *ctx);

typedef struct _nlr_jump_callback_node_t nlr_jump_callback_node_t;

struct _nlr_jump_callback_node_t {
    nlr_jump_callback_node_t *prev;
    nlr_jump_callback_fun_t fun;
};

// Helper macros to save/restore the pystack state
#if MICROPY_ENABLE_PYSTACK
#define MP_NLR_SAVE_PYSTACK(nlr_buf) (nlr_buf)->pystack = MP_STATE_THREAD(pystack_cur)
#define MP_NLR_RESTORE_PYSTACK(nlr_buf) MP_STATE_THREAD(pystack_cur) = (nlr_buf)->pystack
#else
#define MP_NLR_SAVE_PYSTACK(nlr_buf) (void)nlr_buf
#define MP_NLR_RESTORE_PYSTACK(nlr_buf) (void)nlr_buf
#endif

// Helper macro to use at the start of a specific nlr_jump implementation
#define MP_NLR_JUMP_HEAD(val, top) \
    nlr_buf_t **_top_ptr = &MP_STATE_THREAD(nlr_top); \
    nlr_buf_t *top = *_top_ptr; \
    if (top == NULL) { \
        nlr_jump_fail(val); \
    } \
    top->ret_val = val; \
    nlr_call_jump_callbacks(top); \
    MP_NLR_RESTORE_PYSTACK(top); \
    *_top_ptr = top->prev; \

#if !MICROPY_NLR_WASM
    #define NLR_NORETURN NORETURN
#else
    #define NLR_NORETURN 
#endif

#if MICROPY_NLR_SETJMP
// nlr_push() must be defined as a macro, because "The stack context will be
// invalidated if the function which called setjmp() returns."
// For this case it is safe to call nlr_push_tail() first.
#define nlr_push(buf) (nlr_push_tail(buf), setjmp((buf)->jmpbuf))
#else
unsigned int nlr_push(nlr_buf_t *);
#endif

unsigned int nlr_push_tail(nlr_buf_t *top);
void nlr_pop(void);
NLR_NORETURN void nlr_jump(void *val);

#if MICROPY_ENABLE_VM_ABORT
#define nlr_set_abort(buf) MP_STATE_VM(nlr_abort) = buf
#define nlr_get_abort() MP_STATE_VM(nlr_abort)
NORETURN void nlr_jump_abort(void);
#endif

// This must be implemented by a port.  It's called by nlr_jump
// if no nlr buf has been pushed.  It must not return, but rather
// should bail out with a fatal error.
NORETURN void nlr_jump_fail(void *val);

// use nlr_raise instead of nlr_jump so that debugging is easier
#ifndef MICROPY_DEBUG_NLR
#define nlr_raise(val) nlr_jump(MP_OBJ_TO_PTR(val))
#else

#define nlr_raise(val) \
    do { \
        void *_val = MP_OBJ_TO_PTR(val); \
        assert(_val != NULL); \
        assert(mp_obj_is_exception_instance(val)); \
        nlr_jump(_val); \
    } while (0)

#if !MICROPY_NLR_SETJMP
#define nlr_push(val) \
    assert(MP_STATE_THREAD(nlr_top) != val), nlr_push(val)
#endif

#endif

// new exception macros
// nlr_buf nlr;
// NLR_PUSH_BLOCK(nlr) {
//   statement; NLR_CHECK_x();
//   statement; NLR_CHECK_x();
//   statement; NLR_CHECK_x();
// }
// NLR_PUSH_HANDLER(nlr) {
//   exception handler; exception ptr is available at nlr.ret_val or MP_STATE_THREAD(nlr_exc)
// }
#define NLR_PUSH_BLOCK(nlr) nlr_push(&nlr); if (1) 
#define NLR_PUSH_HANDLER(nlr) nlr.ret_val = MP_STATE_THREAD(nlr_exc); MP_STATE_THREAD(nlr_exc) = NULL; if (nlr.ret_val) 

#define NLR_RAISE_RV(val) (nlr_raise(val), return)
#define NLR_RAISE_R0(val) (nlr_raise(val), return 0)
#define NLR_RAISE_R(val, retval) (nlr_raise(val), return retval)

// todo: NLR_RAISE needs a variant for usage inside the NLR_TRY, with goto instead of a return
//       (or maybe we can do this manually after a NLR_RAISE())

// these can be added after calling code which can throw exceptions to terminate execution early
#define NLR_CHECK_RV() if (MP_STATE_THREAD(nlr_exc)) { return; }
#define NLR_CHECK_R0() if (MP_STATE_THREAD(nlr_exc)) { return 0; }
#define NLR_CHECK_R(retval) if (MP_STATE_THREAD(nlr_exc)) { return retval; }

// Push a callback on to the linked-list of NLR jump callbacks.  The `node` pointer must
// be on the C stack.  The `fun` callback will be executed if an NLR jump is taken which
// unwinds the C stack through this `node`.
void nlr_push_jump_callback(nlr_jump_callback_node_t *node, nlr_jump_callback_fun_t fun);

// Pop a callback from the linked-list of NLR jump callbacks.  The corresponding function
// will be called if `run_callback` is true.
void nlr_pop_jump_callback(bool run_callback);

// Pop and call all NLR jump callbacks that were registered after `nlr` buffer was pushed.
void nlr_call_jump_callbacks(nlr_buf_t *nlr);

#endif // MICROPY_INCLUDED_PY_NLR_H
