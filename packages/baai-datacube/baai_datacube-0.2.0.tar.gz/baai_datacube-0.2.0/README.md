    start_time = time.time()
    with tqdm(desc="处理进度", unit='B', unit_scale=True) as pbar:
        with open("../../1949989787863748608_meta.bin", "rb") as fr:
            while True:
                time.sleep(0.03)
                line = fr.readline()
                if not line:
                    break
                pbar.total = Progress().download_count
                pbar.update(1)
                elapsed = time.time() - start_time
                pbar.set_postfix({
                    "已完成": f"{pbar.n}/{pbar.total}",
                    "耗时": f"{elapsed:.1f}s"

                })