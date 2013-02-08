import ctypes


warden = ctypes.windll.warden

def check_revision(archive_name, archive_file_time, seed, header):
    version = ctypes.c_long()
    checksum = ctypes.c_long()
    buf = ctypes.create_string_buffer(warden.crev_max_result())

    ret = warden.check_revision(
        archive_file_time,
        archive_name,
        seed,
        bytes(os.getcwd() + "\\" + "CheckRevision.ini", "ascii"),
        header,
        version,
        checksum,
        buf)
    return (ret, version, checksum, buf.value)

if __name__ == "__main__":
    import os

    print(check_revision(
        b'ver-IX86-3.mpq',
        b'\x80\x9aV\x00p_\xc7\x01',
        b'A=803935755 B=3407199954 C=3485268447 4 A=A^S B=B+C C=C^A A=A-B',
        b"CRev_D2X"
    ))

