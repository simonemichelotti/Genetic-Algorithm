import random
import regex
import os
import re
from pathlib import Path

def generate_simple_pattern():
    """Genera pattern semplici che sicuramente matcheranno molte tracce"""
    patterns = [
        r'[a-z]+',           # Una o più lettere minuscole
        r'[0-9]+',           # Una o più cifre
        r'[a-zA-Z]+',        # Lettere
        r'\d+',              # Cifre
        r'[a-z0-9]+',        # Lettere minuscole e cifre
        r'[a-z]{2,5}',       # 2-5 lettere minuscole
        r'[0-9]{2,4}',       # 2-4 cifre
        r'ab+',              # 'a' seguito da uno o più 'b'
        r'[A-Z]+',           # Una o più lettere maiuscole
        r'[A-Za-z0-9]+',     # Alfanumerico
        r'\w+',              # Caratteri parola
        r'[a-z]{3,}',        # Almeno 3 lettere minuscole
        r'[0-9]{3}',         # Esattamente 3 cifre
        r'abc+',             # 'ab' seguito da uno o più 'c'
        r'x*y+',             # Zero o più 'x' seguito da uno o più 'y'
        r'[aeiou]+',         # Una o più vocali
        r'[bcdfghjklmnpqrstvwxyz]+',  # Consonanti
        r'[aeiou]',          # Una vocale singola
        r'[0-9]{1,2}',       # 1-2 cifre
        r'[a-zA-Z]{4,6}',    # 4-6 lettere
        r'aa+',              # 'a' seguito da uno o più 'a'
        r'123+',             # '12' seguito da uno o più '3'
        r'[xyz]+',           # Una o più x,y,z
        r'[13579]+',         # Cifre dispari
        r'[24680]+',         # Cifre pari
        r'[a-f]+',           # Lettere a-f minuscole
        r'[A-F]+',           # Lettere A-F maiuscole
        r'[a-z0-9]{5,}',     # Almeno 5 caratteri alfanumerici minuscoli
        r'[A-Z0-9]+',        # Maiuscole e cifre
        r'[a-z]{1,3}',       # 1-3 lettere minuscole
        r'[0-9]{5}',         # Esattamente 5 cifre
        r'foo+',             # 'fo' seguito da uno o più 'o'
        r'bar*',             # 'ba' seguito da zero o più 'r'
        r'[pqrs]+',          # Una o più p,q,r,s
        r'[uvw]+',           # Una o più u,v,w
        r'[0-9a-f]+',        # Esadecimale minuscolo
        r'[0-9A-F]+',        # Esadecimale maiuscolo
        r'[a-z]{6,8}',       # 6-8 lettere minuscole
        r'[A-Z]{2,4}',       # 2-4 lettere maiuscole
        r'cat+',             # 'ca' seguito da uno o più 't'
        r'dog*',             # 'do' seguito da zero o più 'g'
        r'[mno]+',           # Una o più m,n,o
        r'[jkl]+',           # Una o più j,k,l
        r'[0-9]{1,5}',       # 1-5 cifre
        r'[a-zA-Z]{1,4}',    # 1-4 lettere
        r'xy+',              # 'x' seguito da uno o più 'y'
        r'pq*',              # 'p' seguito da zero o più 'q'
        r'[def]+',           # Una o più d,e,f
        r'[ghi]+',           # Una o più g,h,i
        r'[0-9]{4}',         # Esattamente 4 cifre
        r'[a-z]{7,}',        # Almeno 7 lettere minuscole
        r'[A-Z]{3,}',        # Almeno 3 lettere maiuscole
        r'zap+',             # 'za' seguito da uno o più 'p'
        r'yum*',             # 'yu' seguito da zero o più 'm'
        r'[stu]+',           # Una o più s,t,u
        r'[vwx]+',           # Una o più v,w,x
        r'[0-9a-z]+',        # Alfanumerico minuscolo
        r'[A-Z0-9]+',        # Maiuscole e cifre
        r'[a-z]{2,}',        # Almeno 2 lettere minuscole
        r'[0-9]{6}',         # Esattamente 6 cifre
        r'frog+',            # 'fro' seguito da uno o più 'g'
        r'lion*',            # 'lio' seguito da zero o più 'n'
        r'[abc]+',           # Una o più a,b,c
        r'[def]+',           # Una o più d,e,f
        r'[0-9]{2,6}',       # 2-6 cifre
        r'[a-zA-Z]{5,}',     # Almeno 5 lettere
        r'vim+',             # 'vi' seguito da uno o più 'm'
        r'wax*',             # 'wa' seguito da zero o più 'x'
        r'[nop]+',           # Una o più n,o,p
        r'[qrs]+',           # Una o più q,r,s
        r'[0-9]{3,5}',       # 3-5 cifre
        r'[a-z]{4,}',        # Almeno 4 lettere minuscole
        r'[A-Z]{1,3}',       # 1-3 lettere maiuscole
        r'yak+',             # 'ya' seguito da uno o più 'k'
        r'zip*',             # 'zi' seguito da zero o più 'p'
        r'[tuv]+',           # Una o più t,u,v
        r'[wxy]+',           # Una o più w,x,y
        r'[0-9a-f]{4,}',     # Almeno 4 caratteri esadecimali
        r'[0-9A-F]{2,}',     # Almeno 2 caratteri esadecimali maiuscoli
        r'[a-z]{5}',         # Esattamente 5 lettere minuscole
        r'[0-9]{7}',         # Esattamente 7 cifre
        r'delta+',           # 'delt' seguito da uno o più 'a'
        r'echo*',            # 'ech' seguito da zero o più 'o'
        r'[fgh]+',           # Una o più f,g,h
        r'[ijk]+',           # Una o più i,j,k
        r'[0-9]{1,3}',       # 1-3 cifre
        r'[a-zA-Z]{6,}',     # Almeno 6 lettere
        r'zeta+',            # 'zet' seguito da uno o più 'a'
        r'omega*',           # 'omeg' seguito da zero o più 'a'
        r'[klm]+',           # Una o più k,l,m
        r'[nop]+',           # Una o più n,o,p
        r'[0-9]{4,6}',       # 4-6 cifre
        r'[a-z]{3,6}',       # 3-6 lettere minuscole
        r'[A-Z]{4,}',        # Almeno 4 lettere maiuscole
        r'alpha+',           # 'alph' seguito da uno o più 'a'
        r'bravo*',           # 'brav' seguito da zero o più 'o'
        r'[rst]+',           # Una o più r,s,t
        r'[uvw]+',           # Una o più u,v,w
        r'[0-9a-z]{3,}',     # Almeno 3 alfanumerici minuscoli
        r'[A-Z0-9]{2,}',     # Almeno 2 maiuscole/cifre
        r'[a-z]{8}',         # Esattamente 8 lettere minuscole
        r'[0-9]{9}',         # Esattamente 9 cifre
        r'echo+',            # 'ech' seguito da uno o più 'o'
        r'foxtrot*',         # 'foxtro' seguito da zero o più 't'
        r'[xyz]+',           # Una o più x,y,z
        r'[abc]+',           # Una o più a,b,c
        r'[0-9]{5,7}',       # 5-7 cifre
        r'[a-zA-Z]{7,}',     # Almeno 7 lettere
        r'golf+',            # 'gol' seguito da uno o più 'f'
        r'hotel*',           # 'hote' seguito da zero o più 'l'
        r'[def]+',           # Una o più d,e,f
        r'[ghi]+',           # Una o più g,h,i
        r'[0-9]{6,8}',       # 6-8 cifre
        r'[a-z]{4,7}',       # 4-7 lettere minuscole
        r'[A-Z]{5,}',        # Almeno 5 lettere maiuscole
        r'[jkl]+',           # Una o più j,k,l
        r'[mno]+',           # Una o più m,n,o
        r'[0-9a-f]{5,}',     # Almeno 5 esadecimali
        r'[0-9A-F]{3,}',     # Almeno 3 esadecimali maiuscoli
        r'[a-z]{9}',         # Esattamente 9 lettere minuscole
        r'[0-9]{10}',        # Esattamente 10 cifre
        r'[xyz]+',           # Una o più x,y,z
        r'[abc]+',           # Una o più a,b,c
        r'[0-9]{5,7}',       # 5-7 cifre
        r'[a-zA-Z]{7,}',     # Almeno 7 lettere
        r'[def]+',           # Una o più d,e,f
        r'[ghi]+',           # Una o più g,h,i
        r'[0-9]{6,8}',       # 6-8 cifre
        r'[a-z]{4,7}',       # 4-7 lettere minuscole
        r'[A-Z]{5,}',        # Almeno 5 lettere maiuscole
        r'[jkl]+',           # Una o più j,k,l
        r'[mno]+',           # Una o più m,n,o
        r'[0-9a-f]{5,}',     # Almeno 5 esadecimali
        r'[0-9A-F]{3,}',     # Almeno 3 esadecimali maiuscoli
        r'[a-z]{9}',         # Esattamente 9 lettere minuscole
        r'[0-9]{10}',        # Esattamente 10 cifre
        r'[xyz]+',           # Una o più x,y,z
        r'[abc]+',           # Una o più a,b,c
        r'[0-9]{5,7}',       # 5-7 cifre
        r'[a-zA-Z]{7,}',     # Almeno 7 lettere
        r'[def]+',           # Una o più d,e,f
        r'[ghi]+',           # Una o più g,h,i
        r'[0-9]{6,8}',       # 6-8 cifre
        r'[a-z]{4,7}',       # 4-7 lettere minuscole
        r'[A-Z]{5,}',        # Almeno 5 lettere maiuscole
        r'[jkl]+',           # Una o più j,k,l
        r'[mno]+',           # Una o più m,n,o
        r'[0-9a-f]{5,}',     # Almeno 5 esadecimali
        r'[0-9A-F]{3,}',     # Almeno 3 esadecimali maiuscoli
        r'[a-z]{9}',         # Esattamente 9 lettere minuscole
        r'[0-9]{10}',        # Esattamente 10 cifre
        r'[pqr]+',           # Una o più p,q,r
        r'[stu]+',           # Una o più s,t,u
        r'[0-9]{7,9}',       # 7-9 cifre
        r'[a-z]{5,8}',       # 5-8 lettere minuscole
        r'[A-Z]{6,}',        # Almeno 6 lettere maiuscole
        r'[vwx]+',           # Una o più v,w,x
        r'[yza]+',           # Una o più y,z,a
        r'[0-9a-f]{6,}',     # Almeno 6 esadecimali
        r'[0-9A-F]{4,}',     # Almeno 4 esadecimali maiuscoli
        r'[a-z]{10}',        # Esattamente 10 lettere minuscole
        r'[0-9]{11}',        # Esattamente 11 cifre
        r'[bcd]+',           # Una o più b,c,d
        r'[efg]+',           # Una o più e,f,g
        r'[0-9]{8,10}',      # 8-10 cifre
        r'[a-zA-Z]{8,}',     # Almeno 8 lettere
        r'[hij]+',           # Una o più h,i,j
        r'[klm]+',           # Una o più k,l,m
        r'[0-9]{9,11}',      # 9-11 cifre
        r'[a-z]{6,9}',       # 6-9 lettere minuscole
        r'[A-Z]{7,}',        # Almeno 7 lettere maiuscole
        r'[nop]+',           # Una o più n,o,p
        r'[qrs]+',           # Una o più q,r,s
        r'[0-9a-f]{7,}',     # Almeno 7 esadecimali
        r'[0-9A-F]{5,}',     # Almeno 5 esadecimali maiuscoli
        r'[a-z]{11}',        # Esattamente 11 lettere minuscole
        r'[0-9]{12}',        # Esattamente 12 cifre
        r'[tuv]+',           # Una o più t,u,v
        r'[wxy]+',           # Una o più w,x,y
        r'[0-9]{10,12}',     # 10-12 cifre
        r'[a-zA-Z]{9,}',     # Almeno 9 lettere
        r'[fgh]+',           # Una o più f,g,h
        r'[ijk]+',           # Una o più i,j,k
        r'[0-9]{11,13}',     # 11-13 cifre
        r'[a-z]{7,10}',      # 7-10 lettere minuscole
        r'[A-Z]{8,}',        # Almeno 8 lettere maiuscole
        r'[lmn]+',           # Una o più l,m,n
        r'[opq]+',           # Una o più o,p,q
        r'[0-9a-f]{8,}',     # Almeno 8 esadecimali
        r'[0-9A-F]{6,}',     # Almeno 6 esadecimali maiuscoli
        r'[a-z]{12}',        # Esattamente 12 lettere minuscole
        r'[0-9]{13}',        # Esattamente 13 cifre
        r'[rst]+',           # Una o più r,s,t
        r'[uvw]+',           # Una o più u,v,w
        r'[0-9]{12,14}',     # 12-14 cifre
        r'[a-zA-Z]{10,}',    # Almeno 10 lettere
        r'[xyz]+',           # Una o più x,y,z
        r'[abc]+',           # Una o più a,b,c
        r'[0-9]{13,15}',     # 13-15 cifre
        r'[a-z]{8,11}',      # 8-11 lettere minuscole
        r'[A-Z]{9,}',        # Almeno 9 lettere maiuscole
        r'[def]+',           # Una o più d,e,f
        r'[ghi]+',           # Una o più g,h,i
        r'[0-9a-f]{9,}',     # Almeno 9 esadecimali
        r'[0-9A-F]{7,}',     # Almeno 7 esadecimali maiuscoli
        r'[a-z]{13}',        # Esattamente 13 lettere minuscole
        r'[0-9]{14}',        # Esattamente 14 cifre
        r'[jkl]+',           # Una o più j,k,l
        r'[mno]+',           # Una o più m,n,o
        r'[0-9]{14,16}',     # 14-16 cifre
        r'[a-zA-Z]{11,}',    # Almeno 11 lettere
        r'[pqr]+',           # Una o più p,q,r
        r'[stu]+',           # Una o più s,t,u
        r'[0-9]{15,17}',     # 15-17 cifre
        r'[a-z]{9,12}',      # 9-12 lettere minuscole
        r'[A-Z]{10,}',       # Almeno 10 lettere maiuscole
        r'[vwx]+',           # Una o più v,w,x
        r'[yza]+',           # Una o più y,z,a
        r'[0-9a-f]{10,}',    # Almeno 10 esadecimali
        r'[0-9A-F]{8,}',     # Almeno 8 esadecimali maiuscoli
        r'[a-z]{14}',        # Esattamente 14 lettere minuscole
        r'[0-9]{15}',        # Esattamente 15 cifre
        r'[bcd]+',           # Una o più b,c,d
        r'[efg]+',           # Una o più e,f,g
        r'[0-9]{16,18}',     # 16-18 cifre
        r'[a-zA-Z]{12,}',    # Almeno 12 lettere
        r'[hij]+',           # Una o più h,i,j
        r'[klm]+',           # Una o più k,l,m
        r'[0-9]{17,19}',     # 17-19 cifre
        r'[a-z]{10,13}',     # 10-13 lettere minuscole
        r'[A-Z]{11,}',       # Almeno 11 lettere maiuscole
        r'[nop]+',           # Una o più n,o,p
        r'[qrs]+',           # Una o più q,r,s
        r'[0-9a-f]{11,}',    # Almeno 11 esadecimali
        r'[0-9A-F]{9,}',     # Almeno 9 esadecimali maiuscoli
        r'[a-z]{15}',        # Esattamente 15 lettere minuscole
        r'[0-9]{16}',        # Esattamente 16 cifre
    ]
    return random.choice(patterns)

def generate_trace_from_pattern(pattern):
    """Genera una traccia che matcha COMPLETAMENTE il pattern"""
    try:
        # Estrai il pattern base
        if pattern == r'[a-z]+':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
        elif pattern == r'[0-9]+':
            return ''.join(random.choices('0123456789', k=random.randint(3, 10)))
        elif pattern == r'[a-zA-Z]+':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 10)))
        elif pattern == r'\d+':
            return ''.join(random.choices('0123456789', k=random.randint(3, 10)))
        elif pattern == r'[a-z0-9]+':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{2,5}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(2, 5)))
        elif pattern == r'[0-9]{2,4}':
            return ''.join(random.choices('0123456789', k=random.randint(2, 4)))
        elif pattern == r'ab+':
            return 'a' + ''.join(random.choices('b', k=random.randint(1, 5)))
        elif pattern == r'[A-Z]+':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 10)))
        elif pattern == r'[A-Za-z0-9]+':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(3, 10)))
        elif pattern == r'\w+':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{3,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
        elif pattern == r'[0-9]{3}':
            return ''.join(random.choices('0123456789', k=3))
        elif pattern == r'abc+':
            return 'ab' + ''.join(random.choices('c', k=random.randint(1, 5)))
        elif pattern == r'x*y+':
            x_count = random.randint(0, 3)
            y_count = random.randint(1, 5)
            return 'x' * x_count + 'y' * y_count
        elif pattern == r'[aeiou]+':
            return ''.join(random.choices('aeiou', k=random.randint(1, 10)))
        elif pattern == r'[bcdfghjklmnpqrstvwxyz]+':
            return ''.join(random.choices('bcdfghjklmnpqrstvwxyz', k=random.randint(3, 10)))
        elif pattern == r'test':
            return 'test'
        elif pattern == r'[aeiou]':
            return random.choice('aeiou')
        elif pattern == r'[0-9]{1,2}':
            return ''.join(random.choices('0123456789', k=random.randint(1, 2)))
        elif pattern == r'[a-zA-Z]{4,6}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(4, 6)))
        elif pattern == r'aa+':
            return 'a' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'123+':
            return '12' + ''.join(random.choices('3', k=random.randint(1, 5)))
        elif pattern == r'[xyz]+':
            return ''.join(random.choices('xyz', k=random.randint(1, 10)))
        elif pattern == r'[13579]+':
            return ''.join(random.choices('13579', k=random.randint(3, 10)))
        elif pattern == r'[24680]+':
            return ''.join(random.choices('24680', k=random.randint(3, 10)))
        elif pattern == r'[a-f]+':
            return ''.join(random.choices('abcdef', k=random.randint(3, 10)))
        elif pattern == r'[A-F]+':
            return ''.join(random.choices('ABCDEF', k=random.randint(3, 10)))
        elif pattern == r'[a-z0-9]{5,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))
        elif pattern == r'[A-Z0-9]+':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{1,3}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(1, 3)))
        elif pattern == r'[0-9]{5}':
            return ''.join(random.choices('0123456789', k=5))
        elif pattern == r'hello':
            return 'hello'
        elif pattern == r'world':
            return 'world'
        elif pattern == r'foo+':
            return 'fo' + ''.join(random.choices('o', k=random.randint(1, 5)))
        elif pattern == r'bar*':
            return 'ba' + ''.join(random.choices('r', k=random.randint(0, 5)))
        elif pattern == r'[pqrs]+':
            return ''.join(random.choices('pqrs', k=random.randint(1, 10)))
        elif pattern == r'[uvw]+':
            return ''.join(random.choices('uvw', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]+':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(3, 10)))
        elif pattern == r'[0-9A-F]+':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{6,8}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(6, 8)))
        elif pattern == r'[A-Z]{2,4}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(2, 4)))
        elif pattern == r'cat+':
            return 'ca' + ''.join(random.choices('t', k=random.randint(1, 5)))
        elif pattern == r'dog*':
            return 'do' + ''.join(random.choices('g', k=random.randint(0, 5)))
        elif pattern == r'[mno]+':
            return ''.join(random.choices('mno', k=random.randint(1, 10)))
        elif pattern == r'[jkl]+':
            return ''.join(random.choices('jkl', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{1,5}':
            return ''.join(random.choices('0123456789', k=random.randint(1, 5)))
        elif pattern == r'[a-zA-Z]{1,4}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(1, 4)))
        elif pattern == r'xy+':
            return 'x' + ''.join(random.choices('y', k=random.randint(1, 5)))
        elif pattern == r'pq*':
            return 'p' + ''.join(random.choices('q', k=random.randint(0, 5)))
        elif pattern == r'[def]+':
            return ''.join(random.choices('def', k=random.randint(1, 10)))
        elif pattern == r'[ghi]+':
            return ''.join(random.choices('ghi', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{4}':
            return ''.join(random.choices('0123456789', k=4))
        elif pattern == r'[a-z]{7,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(7, 10)))
        elif pattern == r'[A-Z]{3,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3, 10)))
        elif pattern == r'zap+':
            return 'za' + ''.join(random.choices('p', k=random.randint(1, 5)))
        elif pattern == r'yum*':
            return 'yu' + ''.join(random.choices('m', k=random.randint(0, 5)))
        elif pattern == r'[stu]+':
            return ''.join(random.choices('stu', k=random.randint(1, 10)))
        elif pattern == r'[vwx]+':
            return ''.join(random.choices('vwx', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-z]+':
            return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
        elif pattern == r'[A-Z0-9]+':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{2,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(2, 10)))
        elif pattern == r'[0-9]{6}':
            return ''.join(random.choices('0123456789', k=6))
        elif pattern == r'quack':
            return 'quack'
        elif pattern == r'zebra':
            return 'zebra'
        elif pattern == r'frog+':
            return 'fro' + ''.join(random.choices('g', k=random.randint(1, 5)))
        elif pattern == r'lion*':
            return 'lio' + ''.join(random.choices('n', k=random.randint(0, 5)))
        elif pattern == r'[abc]+':
            return ''.join(random.choices('abc', k=random.randint(1, 10)))
        elif pattern == r'[def]+':
            return ''.join(random.choices('def', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{2,6}':
            return ''.join(random.choices('0123456789', k=random.randint(2, 6)))
        elif pattern == r'[a-zA-Z]{5,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(5, 10)))
        elif pattern == r'vim+':
            return 'vi' + ''.join(random.choices('m', k=random.randint(1, 5)))
        elif pattern == r'wax*':
            return 'wa' + ''.join(random.choices('x', k=random.randint(0, 5)))
        elif pattern == r'[nop]+':
            return ''.join(random.choices('nop', k=random.randint(1, 10)))
        elif pattern == r'[qrs]+':
            return ''.join(random.choices('qrs', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{3,5}':
            return ''.join(random.choices('0123456789', k=random.randint(3, 5)))
        elif pattern == r'[a-z]{4,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(4, 10)))
        elif pattern == r'[A-Z]{1,3}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(1, 3)))
        elif pattern == r'yak+':
            return 'ya' + ''.join(random.choices('k', k=random.randint(1, 5)))
        elif pattern == r'zip*':
            return 'zi' + ''.join(random.choices('p', k=random.randint(0, 5)))
        elif pattern == r'[tuv]+':
            return ''.join(random.choices('tuv', k=random.randint(1, 10)))
        elif pattern == r'[wxy]+':
            return ''.join(random.choices('wxy', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{4,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(4, 10)))
        elif pattern == r'[0-9A-F]{2,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(2, 10)))
        elif pattern == r'[a-z]{5}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
        elif pattern == r'[0-9]{7}':
            return ''.join(random.choices('0123456789', k=7))
        elif pattern == r'beta':
            return 'beta'
        elif pattern == r'gamma':
            return 'gamma'
        elif pattern == r'delta+':
            return 'delt' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'echo*':
            return 'ech' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[fgh]+':
            return ''.join(random.choices('fgh', k=random.randint(1, 10)))
        elif pattern == r'[ijk]+':
            return ''.join(random.choices('ijk', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{1,3}':
            return ''.join(random.choices('0123456789', k=random.randint(1, 3)))
        elif pattern == r'[a-zA-Z]{6,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(6, 10)))
        elif pattern == r'zeta+':
            return 'zet' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'omega*':
            return 'omeg' + ''.join(random.choices('a', k=random.randint(0, 5)))
        elif pattern == r'[klm]+':
            return ''.join(random.choices('klm', k=random.randint(1, 10)))
        elif pattern == r'[nop]+':
            return ''.join(random.choices('nop', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{4,6}':
            return ''.join(random.choices('0123456789', k=random.randint(4, 6)))
        elif pattern == r'[a-z]{3,6}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 6)))
        elif pattern == r'[A-Z]{4,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(4, 10)))
        elif pattern == r'alpha+':
            return 'alph' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'bravo*':
            return 'brav' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[rst]+':
            return ''.join(random.choices('rst', k=random.randint(1, 10)))
        elif pattern == r'[uvw]+':
            return ''.join(random.choices('uvw', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-z]{3,}':
            return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
        elif pattern == r'[A-Z0-9]{2,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(2, 10)))
        elif pattern == r'[a-z]{8}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
        elif pattern == r'[0-9]{9}':
            return ''.join(random.choices('0123456789', k=9))
        elif pattern == r'charlie':
            return 'charlie'
        elif pattern == r'delta':
            return 'delta'
        elif pattern == r'echo+':
            return 'ech' + ''.join(random.choices('o', k=random.randint(1, 5)))
        elif pattern == r'foxtrot*':
            return 'foxtro' + ''.join(random.choices('t', k=random.randint(0, 5)))
        elif pattern == r'[xyz]+':
            return ''.join(random.choices('xyz', k=random.randint(1, 10)))
        elif pattern == r'[abc]+':
            return ''.join(random.choices('abc', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{5,7}':
            return ''.join(random.choices('0123456789', k=random.randint(5, 7)))
        elif pattern == r'[a-zA-Z]{7,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(7, 10)))
        elif pattern == r'golf+':
            return 'gol' + ''.join(random.choices('f', k=random.randint(1, 5)))
        elif pattern == r'hotel*':
            return 'hote' + ''.join(random.choices('l', k=random.randint(0, 5)))
        elif pattern == r'[def]+':
            return ''.join(random.choices('def', k=random.randint(1, 10)))
        elif pattern == r'[ghi]+':
            return ''.join(random.choices('ghi', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{6,8}':
            return ''.join(random.choices('0123456789', k=random.randint(6, 8)))
        elif pattern == r'[a-z]{4,7}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(4, 7)))
        elif pattern == r'[A-Z]{5,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(5, 10)))
        elif pattern == r'india+':
            return 'indi' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'juliet*':
            return 'julie' + ''.join(random.choices('t', k=random.randint(0, 5)))
        elif pattern == r'[jkl]+':
            return ''.join(random.choices('jkl', k=random.randint(1, 10)))
        elif pattern == r'[mno]+':
            return ''.join(random.choices('mno', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{5,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(5, 10)))
        elif pattern == r'[0-9A-F]{3,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(3, 10)))
        elif pattern == r'[a-z]{9}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=9))
        elif pattern == r'[0-9]{10}':
            return ''.join(random.choices('0123456789', k=10))
        elif pattern == r'kilo+':
            return 'kil' + ''.join(random.choices('o', k=random.randint(1, 5)))
        elif pattern == r'lima*':
            return 'lim' + ''.join(random.choices('a', k=random.randint(0, 5)))
        elif pattern == r'[pqr]+':
            return ''.join(random.choices('pqr', k=random.randint(1, 10)))
        elif pattern == r'[stu]+':
            return ''.join(random.choices('stu', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{7,9}':
            return ''.join(random.choices('0123456789', k=random.randint(7, 9)))
        elif pattern == r'[a-z]{5,8}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 8)))
        elif pattern == r'[A-Z]{6,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(6, 10)))
        elif pattern == r'mike+':
            return 'mik' + ''.join(random.choices('e', k=random.randint(1, 5)))
        elif pattern == r'november*':
            return 'novembe' + ''.join(random.choices('r', k=random.randint(0, 5)))
        elif pattern == r'[vwx]+':
            return ''.join(random.choices('vwx', k=random.randint(1, 10)))
        elif pattern == r'[yza]+':
            return ''.join(random.choices('yza', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{6,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(6, 10)))
        elif pattern == r'[0-9A-F]{4,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(4, 10)))
        elif pattern == r'[a-z]{10}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
        elif pattern == r'[0-9]{11}':
            return ''.join(random.choices('0123456789', k=11))
        elif pattern == r'oscar':
            return 'oscar'
        elif pattern == r'papa':
            return 'papa'
        elif pattern == r'quebec+':
            return 'quebe' + ''.join(random.choices('c', k=random.randint(1, 5)))
        elif pattern == r'romeo*':
            return 'rome' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[bcd]+':
            return ''.join(random.choices('bcd', k=random.randint(1, 10)))
        elif pattern == r'[efg]+':
            return ''.join(random.choices('efg', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{8,10}':
            return ''.join(random.choices('0123456789', k=random.randint(8, 10)))
        elif pattern == r'[a-zA-Z]{8,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(8, 10)))
        elif pattern == r'sierra+':
            return 'sier' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'tango*':
            return 'tang' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[hij]+':
            return ''.join(random.choices('hij', k=random.randint(1, 10)))
        elif pattern == r'[klm]+':
            return ''.join(random.choices('klm', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{9,11}':
            return ''.join(random.choices('0123456789', k=random.randint(9, 11)))
        elif pattern == r'[a-z]{6,9}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(6, 9)))
        elif pattern == r'[A-Z]{7,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(7, 10)))
        elif pattern == r'uniform+':
            return 'unifor' + ''.join(random.choices('m', k=random.randint(1, 5)))
        elif pattern == r'victor*':
            return 'victo' + ''.join(random.choices('r', k=random.randint(0, 5)))
        elif pattern == r'[nop]+':
            return ''.join(random.choices('nop', k=random.randint(1, 10)))
        elif pattern == r'[qrs]+':
            return ''.join(random.choices('qrs', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{7,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(7, 10)))
        elif pattern == r'[0-9A-F]{5,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(5, 10)))
        elif pattern == r'[a-z]{11}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=11))
        elif pattern == r'[0-9]{12}':
            return ''.join(random.choices('0123456789', k=12))
        elif pattern == r'whiskey':
            return 'whiskey'
        elif pattern == r'xray':
            return 'xray'
        elif pattern == r'yankee+':
            return 'yanke' + ''.join(random.choices('e', k=random.randint(1, 5)))
        elif pattern == r'zulu*':
            return 'zul' + ''.join(random.choices('u', k=random.randint(0, 5)))
        elif pattern == r'[tuv]+':
            return ''.join(random.choices('tuv', k=random.randint(1, 10)))
        elif pattern == r'[wxy]+':
            return ''.join(random.choices('wxy', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{10,12}':
            return ''.join(random.choices('0123456789', k=random.randint(10, 12)))
        elif pattern == r'[a-zA-Z]{9,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(9, 10)))
        elif pattern == r'alpha+':
            return 'alph' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'bravo*':
            return 'brav' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[fgh]+':
            return ''.join(random.choices('fgh', k=random.randint(1, 10)))
        elif pattern == r'[ijk]+':
            return ''.join(random.choices('ijk', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{11,13}':
            return ''.join(random.choices('0123456789', k=random.randint(11, 13)))
        elif pattern == r'[a-z]{7,10}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(7, 10)))
        elif pattern == r'[A-Z]{8,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(8, 10)))
        elif pattern == r'charlie+':
            return 'charli' + ''.join(random.choices('e', k=random.randint(1, 5)))
        elif pattern == r'delta*':
            return 'delt' + ''.join(random.choices('a', k=random.randint(0, 5)))
        elif pattern == r'[lmn]+':
            return ''.join(random.choices('lmn', k=random.randint(1, 10)))
        elif pattern == r'[opq]+':
            return ''.join(random.choices('opq', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{8,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(8, 10)))
        elif pattern == r'[0-9A-F]{6,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(6, 10)))
        elif pattern == r'[a-z]{12}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=12))
        elif pattern == r'[0-9]{13}':
            return ''.join(random.choices('0123456789', k=13))
        elif pattern == r'echo':
            return 'echo'
        elif pattern == r'foxtrot':
            return 'foxtrot'
        elif pattern == r'golf+':
            return 'gol' + ''.join(random.choices('f', k=random.randint(1, 5)))
        elif pattern == r'hotel*':
            return 'hote' + ''.join(random.choices('l', k=random.randint(0, 5)))
        elif pattern == r'[rst]+':
            return ''.join(random.choices('rst', k=random.randint(1, 10)))
        elif pattern == r'[uvw]+':
            return ''.join(random.choices('uvw', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{12,14}':
            return ''.join(random.choices('0123456789', k=random.randint(12, 14)))
        elif pattern == r'[a-zA-Z]{10,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(10, 12)))
        elif pattern == r'india+':
            return 'indi' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'juliet*':
            return 'julie' + ''.join(random.choices('t', k=random.randint(0, 5)))
        elif pattern == r'[xyz]+':
            return ''.join(random.choices('xyz', k=random.randint(1, 10)))
        elif pattern == r'[abc]+':
            return ''.join(random.choices('abc', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{13,15}':
            return ''.join(random.choices('0123456789', k=random.randint(13, 15)))
        elif pattern == r'[a-z]{8,11}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(8, 11)))
        elif pattern == r'[A-Z]{9,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(9, 10)))
        elif pattern == r'kilo+':
            return 'kil' + ''.join(random.choices('o', k=random.randint(1, 5)))
        elif pattern == r'lima*':
            return 'lim' + ''.join(random.choices('a', k=random.randint(0, 5)))
        elif pattern == r'[def]+':
            return ''.join(random.choices('def', k=random.randint(1, 10)))
        elif pattern == r'[ghi]+':
            return ''.join(random.choices('ghi', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{9,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(9, 10)))
        elif pattern == r'[0-9A-F]{7,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(7, 10)))
        elif pattern == r'[a-z]{13}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=13))
        elif pattern == r'[0-9]{14}':
            return ''.join(random.choices('0123456789', k=14))
        elif pattern == r'mike':
            return 'mike'
        elif pattern == r'november':
            return 'november'
        elif pattern == r'oscar+':
            return 'osca' + ''.join(random.choices('r', k=random.randint(1, 5)))
        elif pattern == r'papa*':
            return 'pap' + ''.join(random.choices('a', k=random.randint(0, 5)))
        elif pattern == r'[jkl]+':
            return ''.join(random.choices('jkl', k=random.randint(1, 10)))
        elif pattern == r'[mno]+':
            return ''.join(random.choices('mno', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{14,16}':
            return ''.join(random.choices('0123456789', k=random.randint(14, 16)))
        elif pattern == r'[a-zA-Z]{11,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(11, 12)))
        elif pattern == r'quebec+':
            return 'quebe' + ''.join(random.choices('c', k=random.randint(1, 5)))
        elif pattern == r'romeo*':
            return 'rome' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[pqr]+':
            return ''.join(random.choices('pqr', k=random.randint(1, 10)))
        elif pattern == r'[stu]+':
            return ''.join(random.choices('stu', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{15,17}':
            return ''.join(random.choices('0123456789', k=random.randint(15, 17)))
        elif pattern == r'[a-z]{9,12}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(9, 12)))
        elif pattern == r'[A-Z]{10,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(10, 11)))
        elif pattern == r'sierra+':
            return 'sier' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'tango*':
            return 'tang' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[vwx]+':
            return ''.join(random.choices('vwx', k=random.randint(1, 10)))
        elif pattern == r'[yza]+':
            return ''.join(random.choices('yza', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{10,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(10, 11)))
        elif pattern == r'[0-9A-F]{8,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(8, 10)))
        elif pattern == r'[a-z]{14}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=14))
        elif pattern == r'[0-9]{15}':
            return ''.join(random.choices('0123456789', k=15))
        elif pattern == r'uniform':
            return 'uniform'
        elif pattern == r'victor':
            return 'victor'
        elif pattern == r'whiskey+':
            return 'whiske' + ''.join(random.choices('y', k=random.randint(1, 5)))
        elif pattern == r'xray*':
            return 'xra' + ''.join(random.choices('y', k=random.randint(0, 5)))
        elif pattern == r'[bcd]+':
            return ''.join(random.choices('bcd', k=random.randint(1, 10)))
        elif pattern == r'[efg]+':
            return ''.join(random.choices('efg', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{16,18}':
            return ''.join(random.choices('0123456789', k=random.randint(16, 18)))
        elif pattern == r'[a-zA-Z]{12,}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(12, 13)))
        elif pattern == r'yankee+':
            return 'yanke' + ''.join(random.choices('e', k=random.randint(1, 5)))
        elif pattern == r'zulu*':
            return 'zul' + ''.join(random.choices('u', k=random.randint(0, 5)))
        elif pattern == r'[hij]+':
            return ''.join(random.choices('hij', k=random.randint(1, 10)))
        elif pattern == r'[klm]+':
            return ''.join(random.choices('klm', k=random.randint(1, 10)))
        elif pattern == r'[0-9]{17,19}':
            return ''.join(random.choices('0123456789', k=random.randint(17, 19)))
        elif pattern == r'[a-z]{10,13}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(10, 13)))
        elif pattern == r'[A-Z]{11,}':
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(11, 12)))
        elif pattern == r'alpha+':
            return 'alph' + ''.join(random.choices('a', k=random.randint(1, 5)))
        elif pattern == r'bravo*':
            return 'brav' + ''.join(random.choices('o', k=random.randint(0, 5)))
        elif pattern == r'[nop]+':
            return ''.join(random.choices('nop', k=random.randint(1, 10)))
        elif pattern == r'[qrs]+':
            return ''.join(random.choices('qrs', k=random.randint(1, 10)))
        elif pattern == r'[0-9a-f]{11,}':
            return ''.join(random.choices('0123456789abcdef', k=random.randint(11, 12)))
        elif pattern == r'[0-9A-F]{9,}':
            return ''.join(random.choices('0123456789ABCDEF', k=random.randint(9, 10)))
        elif pattern == r'[a-z]{15}':
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=15))
        elif pattern == r'[0-9]{16}':
            return ''.join(random.choices('0123456789', k=16))
        else:
            return None
    except:
        return None

def generate_negative_from_pattern(pattern):
    """Genera una traccia 'near-miss' per il dato pattern (non fullmatch).
    L'obiettivo è che sembri simile alle tracce positive ma non matchi completamente."""
    try:
        if pattern == r'[a-z]+':
            # mostly lowercase but insert a digit or punctuation to break fullmatch
            ln = random.randint(3, 10)
            s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=ln - 1))
            pos = random.randint(0, len(s))
            bad_char = random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_.-')
            return s[:pos] + bad_char + s[pos:]
        elif pattern in (r'[0-9]+', r'\d+'):
            # mostly digits with a letter inserted
            ln = random.randint(3, 10)
            s = ''.join(random.choices('0123456789', k=ln - 1))
            pos = random.randint(0, len(s))
            bad_char = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ._-')
            return s[:pos] + bad_char + s[pos:]
        elif pattern == r'[a-zA-Z]+':
            # letters but include a punctuation
            ln = random.randint(3, 10)
            s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=ln - 1))
            pos = random.randint(0, len(s))
            bad_char = random.choice('0123456789_.-')
            return s[:pos] + bad_char + s[pos:]
        elif pattern == r'[a-z0-9]+':
            # mixed but include symbol or uppercase to break
            ln = random.randint(3, 10)
            s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=ln - 1))
            pos = random.randint(0, len(s))
            bad_char = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*')
            return s[:pos] + bad_char + s[pos:]
        elif pattern == r'[a-z]{2,5}':
            # too short or too long or uppercase
            if random.random() < 0.5:
                return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=1))  # too short
            else:
                return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))  # too long
        elif pattern == r'[0-9]{2,4}':
            if random.random() < 0.5:
                return ''.join(random.choices('0123456789', k=1))
            else:
                s = ''.join(random.choices('0123456789', k=random.randint(5, 8)))
                # Or inject a letter
                pos = random.randint(0, len(s))
                return s[:pos] + random.choice('abcdefghijklmnopqrstuvwxyz') + s[pos:]
        elif pattern == r'ab+':
            # Positive: 'ab', 'abb', ... -> Negatives: 'a' (missing b) or 'ac' or 'xb'
            return random.choice(['a', 'ac', 'xb', 'a' + random.choice('cd')])
        elif pattern == r'test':
            # near-miss words
            candidates = ['tes', 'testt', 'xest', 't3st', 'te-st']
            return random.choice(candidates)
        elif pattern == r'[aeiou]':
            # a consonant or multiple vowels (2)
            return random.choice(['b', 'c', 'xy', 'ab'])
        elif pattern == r'oscar':
            # near-miss words
            candidates = ['osca', 'oscarx', 'xscar', 'osc4r', 'os-car']
            return random.choice(candidates)
        elif pattern == r'papa':
            candidates = ['pap', 'papax', 'xapa', 'pa4a', 'pa-pa']
            return random.choice(candidates)
        elif pattern == r'whiskey':
            candidates = ['whiske', 'whiskeyx', 'xhiskey', 'wh1skey', 'whis-key']
            return random.choice(candidates)
        elif pattern == r'xray':
            candidates = ['xra', 'xrayx', 'xray', 'xr4y', 'x-ra']
            return random.choice(candidates)
        elif pattern == r'uniform':
            candidates = ['unifor', 'uniformx', 'xuniform', 'un1form', 'uni-form']
            return random.choice(candidates)
        elif pattern == r'victor':
            candidates = ['victo', 'victorx', 'xvictor', 'v1ctor', 'vic-tor']
            return random.choice(candidates)
        elif pattern == r'mike':
            candidates = ['mik', 'mikex', 'xmike', 'm1ke', 'mi-ke']
            return random.choice(candidates)
        elif pattern == r'november':
            candidates = ['novembe', 'novemberx', 'xnovember', 'n0vember', 'nov-ember']
            return random.choice(candidates)
        elif pattern == r'echo':
            candidates = ['ech', 'echox', 'xecho', 'e4ho', 'ec-ho']
            return random.choice(candidates)
        elif pattern == r'foxtrot':
            candidates = ['foxtro', 'foxtrotx', 'xfoxtrot', 'f0xtrot', 'fox-trot']
            return random.choice(candidates)
        else:
            # fallback: take a positive and change one char if possible
            positive = generate_trace_from_pattern(pattern)
            if positive:
                # mutate one char to break match
                if len(positive) == 0:
                    return 'x'
                pos = random.randint(0, len(positive) - 1)
                bad_char_pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$'
                bad_char = random.choice(bad_char_pool.replace(positive[pos], ''))
                return positive[:pos] + bad_char + positive[pos + 1:]
    except Exception:
        # fallback: random string with symbols to avoid match
        pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`'
        return ''.join(random.choice(pool) for _ in range(max(1, random.randint(5, 12))))

def generate_random_trace(length=15, trace_type='negative'):
    """Genera una traccia casuale"""
    # keep backward compatible signature; allow pattern-aware generation via kwargs
    # pattern arg optionally used by generator if provided
    return generate_random_trace_fallback(length, trace_type)

def generate_random_trace_fallback(length=15, trace_type='negative', pattern=None):
    """Backward-compatible helper routing generation:
       - positive -> either generate_trace_from_pattern(pattern) or default positive alphanum
       - negative -> try generate_negative_from_pattern(pattern) or fallback to symbol-only negatives
    """
    if trace_type == 'negative':
        if pattern:
            neg = generate_negative_from_pattern(pattern)
            if neg is not None:
                return neg
        # Tracce che NON dovrebbero matchare (solo simboli e maiuscole)
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`€£¥¢§©®™°'
        return ''.join(random.choice(characters) for _ in range(length))
    else:
        if pattern:
            pos = generate_trace_from_pattern(pattern)
            if pos is not None:
                return pos
        characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(characters) for _ in range(length))

# alias old name to maintain exports
generate_random_trace = generate_random_trace_fallback

def create_directories(base_dir=None):
    """Crea le cartelle per le tracce buone e cattive sotto base_dir o project tracce/"""
    if base_dir:
        base_path = Path(base_dir)
    else:
        base_path = Path(__file__).parent / "tracce"
    good_path = base_path / "tracce_buone"
    bad_path = base_path / "tracce_cattive"
    debug_path = base_path / "debug"
    
    # Pulisci le cartelle esistenti and create fresh debug
    for path in [good_path, bad_path, debug_path]:
        if path.exists():
            for file in path.glob('*'):
                try:
                    file.unlink()
                except Exception:
                    pass
        path.mkdir(parents=True, exist_ok=True)
    
    return good_path, bad_path, debug_path

def split_top_level_alternatives(pattern):
    parts = []
    cur = []
    depth = 0
    in_char_class = False
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == '[' and not in_char_class:
            in_char_class = True
            cur.append(ch)
        elif ch == ']' and in_char_class:
            in_char_class = False
            cur.append(ch)
        elif ch == '(' and not in_char_class:
            depth += 1
            cur.append(ch)
        elif ch == ')' and not in_char_class:
            if depth > 0:
                depth -= 1
            cur.append(ch)
        elif ch == '|' and depth == 0 and not in_char_class:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append(''.join(cur))
    return parts

def sanitize_regex_pattern(pattern):
    """Try lightweight fixes for common malformed alternation issues.
    Heuristics:
      - strip leading/trailing pipes
      - collapse consecutive pipes
      - remove empty top-level alternatives
      - drop top-level alternatives that look like flag tokens (e.g. 'g','gm') which are often emitted by buggy converters
    Returns sanitized pattern (may be unchanged)."""
    if pattern is None:
        return pattern
    orig = pattern
    p = pattern.strip()
    # quick trims
    p = re.sub(r'^\|+', '', p)
    p = re.sub(r'\|+$', '', p)
    p = re.sub(r'\|{2,}', '|', p)
    # split top-level alternatives safely
    parts = split_top_level_alternatives(p)
    FLAGS = set('gimuxs')  # common flag letters; 'g' not valid in Python's inline flags, often spurious
    clean_parts = []
    for part in parts:
        part_stripped = part.strip()
        if part_stripped == '':
            # drop empty alternative
            continue
        # drop alternatives that are only composed of flag chars (likely a conversion artifact)
        if re.fullmatch(r'[A-Za-z]+', part_stripped) and all(ch.lower() in FLAGS for ch in part_stripped):
            continue
        clean_parts.append(part)
    if not clean_parts:
        # if we removed everything, fallback to original (we don't want to return empty pattern)
        return orig
    sanitized = '|'.join(clean_parts)
    # final pass to avoid accidental leading/trailing pipes
    sanitized = re.sub(r'^\|+|\|+$', '', sanitized)
    sanitized = re.sub(r'\|{2,}', '|', sanitized)
    return sanitized

def classify_and_save_traces(pattern, selected_per_category=1000, dataset_dir=None, max_attempts=100000):
    """Genera tracce finché non ha almeno selected_per_category buone e cattive.
       Salva anche file di debug nel dataset_dir/debug.
    """
    good_path, bad_path, debug_path = create_directories(base_dir=dataset_dir)
    
    good_list = []
    bad_list = []
    all_generated_good = []
    all_generated_bad = []
    bads_that_match = []
    goods_that_not_match = []
    
    try:
        # Try to sanitize obvious conversion errors before compiling.
        sanitized = sanitize_regex_pattern(pattern)
        # Save original + sanitized for debugging
        try:
            with open(debug_path / "pattern_before_compile.txt", "w", encoding='utf-8') as df:
                df.write(f"original_pattern: {repr(pattern)}\n")
                df.write(f"sanitized_pattern: {repr(sanitized)}\n")
        except Exception:
            # best-effort: ignore file write failures
            pass
        # If sanitize returned something different, try that first.
        try:
            compiled_regex = regex.compile(sanitized)
        except regex.error as e1:
            # If sanitized failed, attempt original so we can report both errors
            try:
                compiled_regex = regex.compile(pattern)
            except Exception as e2:
                raise ValueError(
                    f"pattern not valid. regex.compile failed.\n"
                    f"original pattern: {pattern!r}\n"
                    f"sanitized pattern: {sanitized!r}\n"
                    f"first error (sanitized): {e1}\n"
                    f"second error (original): {e2}"
                )
        except Exception as e:
            raise ValueError(f"pattern '{pattern}' non valido: {e}")
    except Exception:
        raise ValueError(f"pattern '{pattern}' non valido")
    
    traces_generated = 0
    attempts = 0
    
    # Generate good traces first
    print("Generating good traces...")
    while len(good_list) < selected_per_category and attempts < max_attempts:
        attempts += 1
        trace = generate_trace_from_pattern(pattern)
        if trace and trace.strip() != '':
            try:
                if compiled_regex.fullmatch(trace):
                    good_list.append(trace.strip())
                    all_generated_good.append(trace)
                else:
                    goods_that_not_match.append(trace)
            except Exception:
                goods_that_not_match.append(trace)
        traces_generated += 1
        if traces_generated % 1000 == 0:
            print(f"  ✓ {traces_generated} generated (good: {len(good_list)})")
    
    # Then generate bad traces
    print("Generating bad traces...")
    bad_attempts = 0
    while len(bad_list) < selected_per_category and bad_attempts < max_attempts:
        bad_attempts += 1
        # Use random symbols to ensure no match
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`€£¥¢§©®™°'
        trace = ''.join(random.choice(characters) for _ in range(random.randint(5, 16)))
        try:
            if not compiled_regex.fullmatch(trace):
                bad_list.append(trace)
                all_generated_bad.append(trace)
            else:
                bads_that_match.append(trace)
        except Exception:
            bad_list.append(trace)  # if error, treat as bad
            all_generated_bad.append(trace)
        traces_generated += 1
        if traces_generated % 1000 == 0:
            print(f"  ✓ {traces_generated} generated (good: {len(good_list)}, bad: {len(bad_list)})")
    
    # Finalize
    selected_good = good_list[:selected_per_category] if len(good_list) >= selected_per_category else good_list
    selected_bad = bad_list[:selected_per_category] if len(bad_list) >= selected_per_category else bad_list
    
    if len(selected_bad) >= selected_per_category:
        selected_bad = selected_bad[:selected_per_category]
    
    # Save debug collections
    with open(debug_path / "all_generated_good.txt", "w", encoding='utf-8') as f:
        for i, s in enumerate(all_generated_good):
            f.write(f"{i:06d}\t{repr(s)}\n")
    with open(debug_path / "all_generated_bad.txt", "w", encoding='utf-8') as f:
        for i, s in enumerate(all_generated_bad):
            f.write(f"{i:06d}\t{repr(s)}\n")
    # Save mismatch cases to inspect (bad that matched; good that didn't)
    with open(debug_path / "bad_matches_unexpected.txt", "w", encoding='utf-8') as f:
        for i, s in enumerate(bads_that_match):
            f.write(f"{i:06d}\t{repr(s)}\n")
    with open(debug_path / "good_not_matching.txt", "w", encoding='utf-8') as f:
        for i, s in enumerate(goods_that_not_match):
            f.write(f"{i:06d}\t{repr(s)}\n")
    
    # write selected traces to final folders (overwrite)
    for idx, trace in enumerate(selected_good):
        filename = f"{idx:04d}.txt"
        filepath = good_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(trace)
    for idx, trace in enumerate(selected_bad):
        filename = f"{idx:04d}.txt"
        filepath = bad_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(trace)
    
    # Save pattern info for convenience
    info_file = (Path(dataset_dir) if dataset_dir else Path(__file__).parent / "tracce") / 'pattern_info.txt'
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"REGEX PATTERN: {pattern}\n")
        f.write(f"Tracce BUONE: {len(selected_good)}\n")
        f.write(f"Tracce CATTIVE: {len(selected_bad)}\n")
        f.write(f"Traces_generated: {traces_generated}\n")
        f.write(f"Goods_that_not_match: {len(goods_that_not_match)}\n")
        f.write(f"Bad_matches_unexpected: {len(bads_that_match)}\n")
    
    # return summary
    return {
        'pattern': pattern,
        'good_count': len(selected_good),
        'bad_count': len(selected_bad),
        'traces_generated': traces_generated,
        'goods_that_not_match': len(goods_that_not_match),
        'bads_that_match': len(bads_that_match),
        'dataset_dir': str(Path(dataset_dir) if dataset_dir else (Path(__file__).parent / "tracce"))
    }

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("REGEX TRACE GENERATOR & CLASSIFIER")
    print("=" * 70)
    
    # Genera pattern semplice e garantito
    pattern = generate_simple_pattern()
    
    # Genera tracce finché non ha 1000 buone e 1000 cattive
    classify_and_save_traces(pattern, selected_per_category=1000)
