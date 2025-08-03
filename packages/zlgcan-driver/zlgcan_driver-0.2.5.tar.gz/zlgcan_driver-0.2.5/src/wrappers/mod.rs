mod constants;
use constants::*;

use std::sync::{Arc, Mutex};
use pyo3::{exceptions, prelude::*, types::PyDict};
use rs_can::{CanDirect, CanFrame, CanId, CanType};
use zlgcan::{
    can::{CanMessage, ZCanTxMode},
    device::DeriveInfo,
    driver::ZDriver
};

#[pyclass]
#[derive(Default, Clone)]
pub struct ZDeriveInfoPy {
    pub(crate) canfd: bool,
    pub(crate) channels: u8,
}

#[pymethods]
impl ZDeriveInfoPy {
    #[new]
    fn new(canfd: bool, channels: u8) -> Self {
        Self { canfd, channels }
    }
}

impl Into<DeriveInfo> for ZDeriveInfoPy {
    fn into(self) -> DeriveInfo {
        DeriveInfo { canfd: self.canfd, channels: self.channels }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct ZCanDriverWrap {
    pub(crate) inner: Arc<Mutex<ZDriver>>,
}

#[pyclass]
#[derive(Clone)]
pub struct ZCanChlCfgPy {
    pub(crate) chl_type: u8,
    pub(crate) chl_mode: u8,
    pub(crate) bitrate: u32,
    pub(crate) filter: Option<u8>,
    pub(crate) dbitrate: Option<u32>,
    pub(crate) resistance: Option<bool>,
    pub(crate) acc_code: Option<u32>,
    pub(crate) acc_mask: Option<u32>,
    pub(crate) brp: Option<u32>,
}

#[pymethods]
impl ZCanChlCfgPy {
    #[new]
    #[pyo3(signature = (chl_type, chl_mode, bitrate, filter=None, dbitrate=None, resistance=None, acc_code=None, acc_mask=None, brp=None))]
    pub fn new(
        chl_type: u8,
        chl_mode: u8,
        bitrate: u32,
        filter: Option<u8>,
        dbitrate: Option<u32>,
        resistance: Option<bool>,
        acc_code: Option<u32>,
        acc_mask: Option<u32>,
        brp: Option<u32>,
    ) -> Self {
        ZCanChlCfgPy {
            chl_type,
            chl_mode,
            bitrate,
            filter,
            dbitrate,
            resistance,
            acc_code,
            acc_mask,
            brp,
        }
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct ZCanMessagePy {
    pub(crate) timestamp: u64,
    pub(crate) arbitration_id: u32,
    pub(crate) is_extended_id: bool,
    pub(crate) is_remote_frame: bool,
    pub(crate) is_error_frame: bool,
    pub(crate) channel: u8,
    pub(crate) data: Vec<u8>,
    pub(crate) is_fd: bool,
    pub(crate) is_rx: bool,
    pub(crate) bitrate_switch: bool,
    pub(crate) error_state_indicator: bool,
    pub(crate) tx_mode: u8,
}

impl From<CanMessage> for ZCanMessagePy {
    fn from(msg: CanMessage) -> Self {
        let data = Vec::from(msg.data());
        let id = msg.id();
        let is_extended_id = id.is_extended();
        ZCanMessagePy {
            timestamp: msg.timestamp(),
            arbitration_id: id.as_raw(),
            is_extended_id,
            is_remote_frame: msg.is_remote(),
            is_error_frame: msg.is_error_frame(),
            channel: msg.channel(),
            data,
            is_fd: matches!(msg.can_type(), CanType::CanFd),
            is_rx: match msg.direct() {
                CanDirect::Transmit => false,
                CanDirect::Receive => true,
            },
            bitrate_switch: msg.is_bitrate_switch(),
            error_state_indicator: msg.is_error_frame(),
            tx_mode: msg.tx_mode(),
        }
    }
}

impl TryInto<CanMessage> for ZCanMessagePy {
    type Error = PyErr;

    fn try_into(self) -> Result<CanMessage, Self::Error> {
        let mut msg = if self.is_remote_frame {
            CanMessage::new_remote(CanId::from(self.arbitration_id), self.data.len())
        }
        else {
            CanMessage::new(CanId::from(self.arbitration_id), self.data.as_slice())
        }.ok_or(PyErr::new::<exceptions::PyRuntimeError, String>("Can't new CAN message".into()))?;
        msg.set_timestamp(None)
            .set_direct(if self.is_rx { CanDirect::Receive } else { CanDirect::Transmit })
            .set_channel(self.channel)
            .set_tx_mode(ZCanTxMode::try_from(self.tx_mode).map_err(|e| exceptions::PyValueError::new_err(e.to_string()))?)
            .set_can_type(if self.is_fd { CanType::CanFd } else { CanType::Can })
            .set_bitrate_switch(self.bitrate_switch)
            .set_esi(self.error_state_indicator)
            .set_error_frame(self.is_error_frame);
        Ok(msg)
    }
}

impl ZCanMessagePy {
    pub fn to_python<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let can_mod = py.import(PYTHON_CAN)?;
        let message_class = can_mod.getattr(PYTHON_CAN_MESSAGE)?;

        let kwargs = PyDict::new(py);
        kwargs.set_item(TIMESTAMP, self.timestamp as f64 / 1000.)?;
        kwargs.set_item(ARBITRATION_ID, self.arbitration_id)?;
        kwargs.set_item(IS_EFF, self.is_extended_id)?;
        kwargs.set_item(IS_RTR, self.is_remote_frame)?;
        kwargs.set_item(IS_ERR, self.is_error_frame)?;
        kwargs.set_item(CHANNEL, self.channel)?;
        kwargs.set_item(DLC, self.data.len())?;
        kwargs.set_item(DATA, self.data.clone())?;
        kwargs.set_item(IS_CAN_FD, self.is_fd)?;
        kwargs.set_item(IS_RX, self.is_rx)?;
        kwargs.set_item(IS_BRS, self.bitrate_switch)?;
        kwargs.set_item(IS_ESI, self.error_state_indicator)?;

        message_class.call((), Some(&kwargs))
    }

    pub fn from_python<'py>(_py: Python<'py>, py_message: &Bound<'py, PyAny>) -> PyResult<Self> {
        let timestamp: f64 = py_message.getattr(TIMESTAMP)?.extract()?;
        let timestamp = (timestamp * 1000.) as u64;
        let arbitration_id: u32 = py_message.getattr(ARBITRATION_ID)?.extract()?;
        let is_extended_id: bool = py_message.getattr(IS_EFF)?.extract()?;
        let is_remote_frame: bool = py_message.getattr(IS_RTR)?.extract()?;
        let is_error_frame: bool = py_message.getattr(IS_ERR)?.extract()?;
        let channel: Option<u8> = py_message.getattr(CHANNEL)?.extract()?;
        let data: Vec<u8> = py_message.getattr(DATA)?.extract()?;
        let is_fd: bool = py_message.getattr(IS_CAN_FD)?.extract()?;
        let is_rx: bool = py_message.getattr(IS_RX)?.extract()?;
        let bitrate_switch: bool = py_message.getattr(IS_BRS)?.extract()?;
        let error_state_indicator: bool = py_message.getattr(IS_ESI)?.extract()?;

        Ok(ZCanMessagePy {
            timestamp,
            arbitration_id,
            is_extended_id,
            is_remote_frame,
            is_error_frame,
            channel: channel.unwrap_or(0),
            data,
            is_fd,
            is_rx,
            bitrate_switch,
            error_state_indicator,
            tx_mode: 0,
        })
    }
}
