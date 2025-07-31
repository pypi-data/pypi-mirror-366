import typing, enum, vspyx

@enum.unique
class ServiceId(enum.IntEnum):
	Unknown = 0
	ResponseFlag = 64
	NegativeResponse = 127
	SessionControl = 16
	EcuReset = 17
	ClearDtcs = 20
	ReadDtcs = 25
	ReadDataById = 34
	ReadMemoryByAddress = 35
	SecurityAccess = 39
	CommControl = 40
	ReadDataByPeriodicId = 42
	WriteDataById = 46
	IoControlById = 47
	RoutineControl = 49
	RequestDownload = 52
	RequestUpload = 53
	TransferData = 54
	RequestTransferExit = 55
	RequestFileTransfer = 56
	WriteMemoryByAddress = 61
	TesterPresent = 62
	ControlDtcSetting = 133

@enum.unique
class TransmissionMode(enum.IntEnum):
	Unknown = 0
	SendAtSlowRate = 1
	SendAtMediumRate = 2
	SendAtFastRate = 3
	StopSending = 4

@enum.unique
class FileTransfer_ModeOfOperation(enum.IntEnum):
	Unknown = 0
	FileAdd = 1
	FileDelete = 2
	FileReplace = 3
	FileRead = 4
	DirRead = 5
	FileResume = 6

@enum.unique
class DTCFormatIdentifier(enum.IntEnum):
	SAE_J2012_DA_00 = 0
	ISO_14229_1 = 1
	SAE_J1939_73 = 2
	ISO_11992_4 = 3
	SAE_J2012_DA_04 = 4

class DtcInfo:
	"""DtcInfo
	"""
	Code: int
	Status: typing.Any
	def assign(self, arg0: vspyx.Diagnostics.ISO14229_Services.DtcInfo) -> vspyx.Diagnostics.ISO14229_Services.DtcInfo: ...

	def __str__(self) -> str: ...

class DTC_ISO_14229_1(vspyx.Diagnostics.ISO14229_Services.DtcInfo):
	"""DTC_ISO_14229_1
	"""
	def __str__(self) -> str: ...

class DTC_ISO_15031_6(vspyx.Diagnostics.ISO14229_Services.DtcInfo):
	"""DTC_ISO_15031_6
	"""
	def __str__(self) -> str: ...

class Service:
	"""Service
	"""
	SECURITY_ANY: int
	SUBFUNCTION_SUPPRESS_RESPONSE: int
	ServiceSpecificChecks: vspyx.Core.Function_9c83a5b671
	DoService: vspyx.Core.Function_ef21eb8ca9
	Name: str
	P4ServerMax: typing.Any
	RequestDecoder: vspyx.Core.Function_0eb0e68809
	ResponseDecoder: vspyx.Core.Function_0eb0e68809
	ResponseServiceId: vspyx.Diagnostics.ISO14229_Services.ServiceId
	SecurityMask: int
	ServiceId: vspyx.Diagnostics.ISO14229_Services.ServiceId
	SupportedSessions: typing.List[int]
	SupportedSubfunctions: typing.List[int]

	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> typing.Any: ...


	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> typing.Any: ...


	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> typing.Any: ...

	def InvokeDecoderResolver(self, isResponse: bool, pdu: typing.Any, message: vspyx.Dissector.Message) -> vspyx.Diagnostics.ISO14229_Services.Message: ...

	def Execute(self, message: vspyx.Diagnostics.ISO14229_Services.Message) -> vspyx.Diagnostics.ISO14229_Services.Message: ...

	def IsServiceIdMatch(self, sid: int) -> bool: ...

	def IsResponseRequired(self, data: typing.List[int]) -> bool: ...

	def IsSessionSupported(self, sessionId: int) -> bool: ...

	def IsSubfunctionSupported(self, subfunction: int, sessionId: typing.Any) -> bool: ...

	def VetServiceSpecificChecks(self, pdu: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Nrc: ...

class ServiceConfig:
	"""ServiceConfig
	"""

	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...


	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...


	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...

	def GetService(self, sid: typing.Any, name: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.Service: ...

	def ResolveDecoder(self, sid: vspyx.Diagnostics.ISO14229_Services.ServiceId, pdu: typing.Any, message: vspyx.Dissector.Message) -> vspyx.Diagnostics.ISO14229_Services.Message: ...

class Message:
	"""Message
	"""
	PDU: typing.Any
	Dissection: vspyx.Dissector.Message
	IsNegativeResponse: bool
	IsPositiveResponseSuppressedSpecified: bool
	SID: vspyx.Diagnostics.ISO14229_Services.ServiceId
	Service: vspyx.Diagnostics.ISO14229_Services.Service
	def AssociateService(self, service: vspyx.Diagnostics.ISO14229_Services.Service) -> typing.Any: ...

	def ToRaw(self) -> vspyx.Core.BytesView: ...

class TransactionResults:
	"""TransactionResults
	"""
	StartTime: typing.Any
	EndTime: typing.Any
	RequestPDU: typing.Any
	Responses: typing.List[vspyx.Diagnostics.ISO14229_Services.Message]
	IsValid: bool
	Duration: typing.Any
	RequestMessageSize: int
	TotalResponseMessagesSize: int

class MessageWithSubfunction(vspyx.Diagnostics.ISO14229_Services.Message):
	"""MessageWithSubfunction
	"""
	IsPositiveResponseSuppressedSpecified: bool
	Subfunction: int

class NegativeResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""NegativeResponse
	"""
	FailedSID: vspyx.Diagnostics.ISO14229_Services.ServiceId
	IsNegativeResponse: bool
	NRC: vspyx.Diagnostics.ISO14229_1.Nrc

class SessionControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SessionControlRequest
	"""
	SessionType: int

class SessionControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SessionControlResponse
	"""
	P2ServerMax: int
	P2StarServerMax: int
	SessionType: int

class EcuResetRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""EcuResetRequest
	"""
	ResetType: int

class EcuResetResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""EcuResetResponse
	"""
	PowerDownTime: typing.Any
	ResetType: int

class ClearDtcsRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ClearDtcsRequest
	"""
	GroupInfo: int
	MemorySelection: typing.Any

class ClearDtcsResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ClearDtcsResponse
	"""

class ReadDtcsRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ReadDtcsRequest
	"""
	DtcMask: int
	RecordNumber: int
	SeverityMask: int
	StatusMask: int

class ReadDtcsResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ReadDtcsResponse
	"""
	def AddDtcRecord(self, isByDtcNr: bool, dtc: int, status: typing.Any, dataRecordNr: typing.Any, dataRecordIdentifierCount: typing.Any) -> typing.Any: ...

	def AddDtcAndStatus(self, dtc: int, status: typing.Any) -> typing.Any: ...

	def AddDtcSeverityRecord(self, dtc: int, status: int, severity: int, functionalUnit: typing.Any) -> typing.Any: ...

	def AddDtcFaultCountRecord(self, dtc: int, faultCount: int) -> typing.Any: ...

	def AddDataRecordHeader(self, dataRecordNr: int, dataRecordIdentifierCount: typing.Any) -> typing.Any: ...

	def AddDataRecord(self, dataId: typing.Any, data: typing.List[int]) -> typing.Any: ...

	def AddRecord(self, record: typing.List[int]) -> typing.Any: ...

	def GetDtcCountInfo(self) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcCountInfo: ...

	def GetDtcStatusInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcStatusInfo: ...

	def GetSnapshotIdentificationInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSnapshotIdentificationInfo: ...

	def GetDtcSeverityInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSeverityInfo: ...

	def GetExtOrSnapshotDataInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> typing.Any: ...

	class DtcCountInfo:
		"""DtcCountInfo
		"""
		StatusAvailabilityMask: int
		FormatIdentifier: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier
		Count: int


	class DtcStatusInfo:
		"""DtcStatusInfo
		"""
		StatusAvailabilityMask: int
		Dtcs: typing.List[vspyx.Diagnostics.ISO14229_Services.DtcInfo]


	class DtcSnapshotIdentificationInfo:
		"""DtcSnapshotIdentificationInfo
		"""
		Records: typing.List[vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSnapshotIdentificationInfo.SnapshotNumberPair]
		def AddRecord(self, dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo, snapshotNumber: int) -> typing.Any: ...

		class SnapshotNumberPair:
			"""SnapshotNumberPair
			"""
			Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo
			SnapshotRecordNumber: int



	class DtcSeverityRecord:
		"""DtcSeverityRecord
		"""
		Severity: int
		FunctionalUnit: int
		Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo


	class DtcSeverityInfo:
		"""DtcSeverityInfo
		"""
		StatusAvailabilityMask: int
		Records: typing.List[vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSeverityRecord]
		def AddRecord(self, severity: int, functionalUnit: int, dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo) -> typing.Any: ...


	class DtcDataInfo:
		"""DtcDataInfo
		"""
		IsSnapshotData: bool
		Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo
		CurrentRecordNumber: typing.Any
		CurrentSnapshotIdentifier: typing.Any
		CurrentSnapshotIdentifierCount: typing.Any
		HasData: bool
		HasRecord: bool
		def GetCurrentData(self, dataSize: int) -> typing.Any: ...

		def NextRecord(self) -> bool: ...

		def NextData(self, recordSize: int) -> bool: ...


class ReadDataByIdRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadDataByIdRequest
	"""
	Ids: typing.List[int]

class ReadDataByIdResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadDataByIdResponse
	"""
	DataStart: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle
	def ReadId(self, handle: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle) -> int: ...

	def ReadParameterData(self, handle: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle, size: int) -> vspyx.Core.BytesView: ...

	def WriteId(self, did: int) -> typing.Any: ...

	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

	class RecordHandle:
		"""RecordHandle
		"""
		CurrentOffset: int
		Size: int
		def IsValid(self) -> bool: ...


class ReadOrWriteMemoryByAddressMessage(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadOrWriteMemoryByAddressMessage
	"""
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class ReadMemoryByAddressRequest(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""ReadMemoryByAddressRequest
	"""

class ReadMemoryByAddressResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadMemoryByAddressResponse
	"""
	Data: vspyx.Core.BytesView
	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

class WriteMemoryByAddressRequest(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""WriteMemoryByAddressRequest
	"""
	Data: vspyx.Core.BytesView
	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

class WriteMemoryByAddressResponse(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""WriteMemoryByAddressResponse
	"""

class SecurityAccessRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SecurityAccessRequest
	"""
	IsSeedRequest: bool
	Level: int
	Parameter: vspyx.Core.BytesView
	SecurityAccessType: int

class SecurityAccessResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SecurityAccessResponse
	"""
	IsSeedRequest: bool
	Level: int
	Parameter: vspyx.Core.BytesView
	SecurityAccessType: int

class CommControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""CommControlRequest
	"""
	CommSubnet: int
	CommType: int
	ControlType: int
	NodeId: int

class CommControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""CommControlResponse
	"""
	ControlType: int

class ReadDataByPeriodicIdRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadDataByPeriodicIdRequest
	"""
	Ids: vspyx.Core.BytesView
	TransmissionMode: vspyx.Diagnostics.ISO14229_Services.TransmissionMode

class ReadDataByPeriodicIdResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""ReadDataByPeriodicIdResponse
	"""

class WriteDataByIdRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""WriteDataByIdRequest
	"""
	DataId: int
	Parameter: vspyx.Core.BytesView

class WriteDataByIdResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""WriteDataByIdResponse
	"""
	DataId: int

class IoControlByIdRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""IoControlByIdRequest
	"""
	ControlType: int
	DataId: int
	Parameter: vspyx.Core.BytesView

class IoControlByIdResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""IoControlByIdResponse
	"""
	DataId: int
	Parameter: vspyx.Core.BytesView
	Status: int

class RoutineControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""RoutineControlRequest
	"""
	OptionData: vspyx.Core.BytesView
	RoutineId: int

class RoutineControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""RoutineControlResponse
	"""
	RoutineId: int
	StatusData: vspyx.Core.BytesView

class RequestDownloadRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestDownloadRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class RequestDownloadResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestDownloadResponse
	"""
	LengthFormat: int
	MaxBlockLength: int

class RequestUploadRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestUploadRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class RequestUploadResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestUploadResponse
	"""
	LengthFormat: int
	MaxBlockLength: int

class TransferDataRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""TransferDataRequest
	"""
	BlockSequenceCounter: int
	Data: vspyx.Core.BytesView

class TransferDataResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""TransferDataResponse
	"""
	BlockSequenceCounter: int
	Data: vspyx.Core.BytesView

class RequestTransferExitRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestTransferExitRequest
	"""
	Parameter: vspyx.Core.BytesView

class RequestTransferExitResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestTransferExitResponse
	"""
	Parameter: vspyx.Core.BytesView

class RequestFileTransferRequest(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestFileTransferRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	FilePathAndName: vspyx.Core.BytesView
	FileSizeCompressed: int
	FileSizeUnCompressed: int
	ModeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation

class RequestFileTransferResponse(vspyx.Diagnostics.ISO14229_Services.Message):
	"""RequestFileTransferResponse
	"""
	CompressionMethod: int
	EncryptionMethod: int
	FileSizeCompressed: int
	FileSizeUnCompressed: int
	MaxBlockLength: int
	ModeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation

class TesterPresentRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""TesterPresentRequest
	"""

class TesterPresentResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""TesterPresentResponse
	"""

class ControlDtcSettingRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ControlDtcSettingRequest
	"""
	DtcsSettingType: int
	Parameter: vspyx.Core.BytesView

class ControlDtcSettingResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ControlDtcSettingResponse
	"""
	DtcsSettingType: int

