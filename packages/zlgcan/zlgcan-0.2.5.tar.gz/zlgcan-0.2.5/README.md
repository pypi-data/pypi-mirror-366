![PyPI Downloads](https://static.pepy.tech/badge/zlgcan)
![PyPI Downloads](https://static.pepy.tech/badge/zlgcan/month)

# ZLGCAN驱动及集成到python-can(不支持32位)

1. 准备
    * 确保安装相关驱动(USBCAN-I/II驱动得额外安装)
    * 确保安装相[VC++运行环境](https://manual.zlg.cn/web/#/152?page_id=5332)
    * 下载[library](https://github.com/jesses2025smith/rust-can/tree/zlg-lib)文件夹(里面包含[bitrate.cfg.yaml](https://github.com/jesses2025smith/rust-can/tree/zlg-lib/library/bitrate.cfg.yaml))
    * 库文件示例:
      ```shell
      library
        ├──bitrate.cfg.yaml
        ├──linux
        │  └─x86_64
        └─windows
           └─x86_64
      ```
    * 在初始化can.Bus的时候指定zlgcan库路径(0.2.x移除了`zcan.env`配置), 默认为相对工程运行文件同级目录下`library`
      ```python
      libpath=r"C:\your\library\path"
      ```

2. 安装zlgcan(不建议使用低于0.2.0版本)

    ```shell
    pip install zlgcan >= 0.2.0
    ```

3. 使用:
   ```python
   import can
   from zlgcan.zlgcan import ZCanTxMode, ZCANDeviceType
   
   with can.Bus(interface="zlgcan", device_type=ZCANDeviceType.ZCAN_USBCANFD_200U,
                libpath="library/",
                configs=[{'bitrate': 500000, 'resistance': 1}, {'bitrate': 500000, 'resistance': 1}]) as bus:
       bus.send(can.Message(
           arbitration_id=0x123,
           is_extended_id=False,
           channel=0,
           data=[0x01, 0x02, 0x03, ],
           dlc=3,
       ), tx_mode=ZCanTxMode.SELF_SR)
   
       # time.sleep(0.1)
       _msg = bus.recv()
       print(_msg)
   ```

4. CAN测试列表：
   * USBCAN-I-mini - ZCAN_USBCAN1, ZCAN_USBCAN2
   * USBCAN-4E-U - ZCAN_USBCAN_4E_U
   * USBCANFD-100U-mini - ZCAN_USBCANFD_MINI
   * USBCANFD-100U - ZCAN_USBCANFD_100U
   * USBCANFD-200U - ZCAN_USBCANFD_200U
   * USBCANFD-800U - ZCAN_USBCANFD_800U

5. 注意事项:
   * ZCAN_USBCAN1及ZCAN_USBCAN2类型的设备无论是windows还是Linux, 波特率支持均在`bitrate.cfg.yaml`中配置
     * 此时计算timing0及timing1请下载[CAN波特率计算软件](https://zlg.cn/can/down/down/id/22.html)
     * `bitrate.cfg.yaml`文件中USBCANFD设备只配置了500k及1M的波特率, 如需使用其他波特率, 请自行添加
   * 其他CANFD类型的CAN卡仅仅在Linux上使用时`bitrate.cfg.yaml`中配置
     * 此时计算相关值可以通过`ZCANPRO`软件
   * 在Linux上使用ZCAN_USBCAN1衍生CAN卡时, 请在初始化时候设置`ZCanDeriveInfo`信息
   * 该库主要依赖[rust-can](https://github.com/jesses2025smith/rust-can),如有问题,请提[issue](https://github.com/jesses2025smith/rust-can/issues/new)

6. 官方工具及文档:
   * [工具下载](https://zlg.cn/can/down/down/id/22.html)
   * [驱动下载](https://manual.zlg.cn/web/#/146)
   * [二次开发文档](https://manual.zlg.cn/web/#/42/1710)
   * [二次开发文档CANFD-Linux](https://manual.zlg.cn/web/#/188/6982)
   * [二次开发Demo](https://manual.zlg.cn/web/#/152/5332)

