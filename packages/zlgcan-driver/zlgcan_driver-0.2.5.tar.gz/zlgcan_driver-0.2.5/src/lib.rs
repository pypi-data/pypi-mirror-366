pub(crate) mod wrappers;

use std::sync::{Arc, Mutex};
use pyo3::{exceptions, prelude::*};
use rs_can::{CanError, CanFrame, CanType, ChannelConfig, DeviceBuilder};
use zlgcan::{*, can::*, device::*, driver::*};
use crate::wrappers::{ZCanChlCfgPy, ZCanDriverWrap, ZCanMessagePy, ZDeriveInfoPy};

#[pyfunction]
fn convert_to_python<'py>(py: Python<'py>, rust_message: ZCanMessagePy) -> PyResult<Bound<'py, PyAny>> {
    rust_message.to_python(py)
}

#[allow(dead_code)]
#[pyfunction]
fn convert_from_python<'py>(py: Python<'py>, py_message: &Bound<'py, PyAny>) -> PyResult<ZCanMessagePy> {
    ZCanMessagePy::from_python(py, py_message)
}

#[pyfunction]
fn zlgcan_init_can(
    libpath: String,
    dev_type: u32,
    dev_idx: u32,
    cfgs: Vec<ZCanChlCfgPy>,
    derive_info: Option<ZDeriveInfoPy>,
) -> PyResult<ZCanDriverWrap> {
    let dev_type = ZCanDeviceType::try_from(dev_type)
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    let mut builder = DeviceBuilder::new();
    builder
        .add_other(LIBPATH, Box::new(libpath))
        .add_other(DEVICE_TYPE, Box::new(dev_type))
        .add_other(DEVICE_INDEX, Box::new(dev_idx));
    derive_info.map(
        |info| builder.add_other(DERIVE_INFO, Box::<DeriveInfo>::new(info.into()))
    );

    for (i, cfg) in cfgs.into_iter().enumerate() {
        let chl_type = ZCanChlType::try_from(cfg.chl_type)
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
        let chl_mode = ZCanChlMode::try_from(cfg.chl_mode)
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
        let mut c = ChannelConfig::new(cfg.bitrate);
        c.add_other(CHANNEL_TYPE, Box::new(chl_type))
            .add_other(CHANNEL_MODE, Box::new(chl_mode));

        cfg.dbitrate.map(|dbitrate| c.set_data_bitrate(dbitrate));
        cfg.resistance.map(|resistance| c.set_resistance(resistance));
        cfg.filter.map(|filter| c.add_other(FILTER_TYPE, Box::new(filter)));
        cfg.acc_code.map(|acc_code| c.add_other(ACC_CODE, Box::new(acc_code)));
        cfg.acc_mask.map(|acc_mask| c.add_other(ACC_MASK, Box::new(acc_mask)));
        cfg.brp.map(|brp| c.add_other(BRP, Box::new(brp)));

        builder.add_config(i as u8, c);
    }

    let device = builder.build::<ZDriver>()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;

    Ok(ZCanDriverWrap { inner: Arc::new(Mutex::new(device)) })
}

#[pyfunction]
fn zlgcan_device_info(device: &ZCanDriverWrap) -> PyResult<String> {
    let device = device.inner.lock()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    Ok(
        device.device_info()
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?
            .to_string()
    )
}

#[pyfunction]
fn zlgcan_clear_can_buffer(
    device: &ZCanDriverWrap,
    channel: u8,
) -> PyResult<()> {
    let device = device.inner.lock()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    device.clear_can_buffer(channel)
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))
}

#[pyfunction]
fn zlgcan_send(
    device: &ZCanDriverWrap,
    msg: ZCanMessagePy,
) -> PyResult<u32> {
    let device = device.inner.lock()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    let message: CanMessage = msg.try_into()?;
    match message.can_type() {
        CanType::Can => device.transmit_can(message.channel(), vec![message, ])
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string())),
        CanType::CanFd => device.transmit_canfd(message.channel(), vec![message, ])
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string())),
        CanType::CanXl => Err(exceptions::PyValueError::new_err(CanError::NotSupportedError.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (device, channel, timeout=None))]
fn zlgcan_recv<'py>(
    device: &ZCanDriverWrap,
    channel: u8,
    timeout: Option<u32>,
) -> PyResult<Vec<ZCanMessagePy>> {
    let device = device.inner.lock()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;

    let can_cnt = device.get_can_num(channel, ZCanFrameType::CAN)
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    let canfd_cnt = device.get_can_num(channel, ZCanFrameType::CANFD)
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    let mut results = Vec::with_capacity((can_cnt + canfd_cnt) as usize);

    if can_cnt > 0 {
        let mut can_frames = device.receive_can(channel, can_cnt, timeout)
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
        results.append(&mut can_frames);
    }
    if canfd_cnt > 0 {
        let mut canfd_frames = device.receive_canfd(channel, canfd_cnt, timeout)
            .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
        results.append(&mut canfd_frames);
    }

    Ok(results.into_iter()
        .map(ZCanMessagePy::from)
        .collect::<Vec<_>>())
}

#[pyfunction]
fn zlgcan_close(
    device: &ZCanDriverWrap
) -> PyResult<()> {
    let mut device = device.inner.lock()
        .map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?;
    device.close();
    Ok(())
}

#[pyfunction]
fn set_message_mode(msg: &mut ZCanMessagePy, mode: u8) {
    msg.tx_mode = mode;
}

// 此方法名必须与Cargo.toml-[lib]配置下name保持一致
#[pymodule]
fn zlgcan_driver(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ZCanChlCfgPy>()?;
    m.add_class::<ZCanMessagePy>()?;
    m.add_class::<ZDeriveInfoPy>()?;
    m.add_class::<ZCanDriverWrap>()?;

    m.add_function(wrap_pyfunction!(convert_to_python, m)?)?;
    m.add_function(wrap_pyfunction!(convert_from_python, m)?)?;
    m.add_function(wrap_pyfunction!(set_message_mode, m)?)?;

    m.add_function(wrap_pyfunction!(zlgcan_init_can, m)?)?;
    m.add_function(wrap_pyfunction!(zlgcan_device_info, m)?)?;
    m.add_function(wrap_pyfunction!(zlgcan_clear_can_buffer, m)?)?;
    m.add_function(wrap_pyfunction!(zlgcan_send, m)?)?;
    m.add_function(wrap_pyfunction!(zlgcan_recv, m)?)?;
    m.add_function(wrap_pyfunction!(zlgcan_close, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use zlgcan::{
        can::{ZCanChlMode, ZCanChlType},
        device::ZCanDeviceType,
    };
    use super::*;

    #[test]
    fn test_receive() -> anyhow::Result<()> {
        pyo3::prepare_freethreaded_python();

        let dev_type = ZCanDeviceType::ZCAN_USBCANFD_200U as u32;
        let dev_idx = 0;
        let cfg = ZCanChlCfgPy::new(
            ZCanChlType::CAN as u8,
            ZCanChlMode::Normal as u8,
            500_000,
            None,
            None,
            None,
            None,
            None,
            None,
        );
        let cfg2 = ZCanChlCfgPy::new(
            ZCanChlType::CAN as u8,
            ZCanChlMode::Normal as u8,
            500_000,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        let device = zlgcan_init_can("../../RustRoverProjects/rust-can/zlgcan/library".into(), dev_type, dev_idx, vec![cfg, cfg2], None)?;
        let dev_info = zlgcan_device_info(&device)?;
        println!("{}", dev_info);
        std::thread::sleep(std::time::Duration::from_secs(1));

        let mut msg = CanMessage::new(0x7df, &vec![0x02, 0x10, 0x01]).unwrap();
        msg.set_channel(0);
        let ret = zlgcan_send(&device, msg.into())?;
        println!("send: {}", ret);

        std::thread::sleep(std::time::Duration::from_micros(200));
        let msgs = zlgcan_recv(&device, 1, None)?;
        if !msgs.is_empty() {
            println!("{:?}", msgs);
        }

        zlgcan_close(&device)?;

        Ok(())
    }
}
