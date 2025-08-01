// _audio_devices.cpp
#include <Python.h>
#include <mmdeviceapi.h>
#include <functiondiscoverykeys_devpkey.h>
#include <atlbase.h>
#include <propvarutil.h>
#include <audioclient.h>

// 基本的なUID形式での出力（macOSの list_device_uids に対応）
static PyObject* list_device_uids(PyObject* self, PyObject* args) {
    PyObject* device_list = PyList_New(0);
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) return device_list;

    CComPtr<IMMDeviceEnumerator> pEnum;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL, IID_PPV_ARGS(&pEnum));
    if (FAILED(hr)) {
        CoUninitialize();
        return device_list;
    }

    // 入力デバイス（キャプチャ）
    CComPtr<IMMDeviceCollection> pInputColl;
    hr = pEnum->EnumAudioEndpoints(eCapture, DEVICE_STATE_ACTIVE, &pInputColl);
    if (SUCCEEDED(hr)) {
        UINT count = 0;
        pInputColl->GetCount(&count);
        for (UINT i = 0; i < count; ++i) {
            CComPtr<IMMDevice> pDevice;
            if (SUCCEEDED(pInputColl->Item(i, &pDevice))) {
                // デバイス名を取得
                CComPtr<IPropertyStore> pProps;
                WCHAR nameBuffer[256] = L"Unknown Device";
                if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                    PROPVARIANT varName;
                    PropVariantInit(&varName);
                    if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                        if (varName.vt == VT_LPWSTR) {
                            wcscpy_s(nameBuffer, 256, varName.pwszVal);
                        }
                        PropVariantClear(&varName);
                    }
                }

                // デバイスIDを取得
                LPWSTR id = NULL;
                WCHAR idBuffer[512] = L"unknown-id";
                if (SUCCEEDED(pDevice->GetId(&id))) {
                    wcscpy_s(idBuffer, 512, id);
                    CoTaskMemFree(id);
                }

                // "devicename: deviceid" 形式の文字列を作成
                WCHAR result[768];
                swprintf_s(result, 768, L"%s: %s", nameBuffer, idBuffer);
                
                // Unicodeからchar*への変換
                char utf8Result[768 * 3]; // UTF-8は最大3バイト/文字
                WideCharToMultiByte(CP_UTF8, 0, result, -1, utf8Result, sizeof(utf8Result), NULL, NULL);
                
                PyList_Append(device_list, PyUnicode_FromString(utf8Result));
            }
        }
    }

    // 出力デバイス（レンダー）
    CComPtr<IMMDeviceCollection> pOutputColl;
    hr = pEnum->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &pOutputColl);
    if (SUCCEEDED(hr)) {
        UINT count = 0;
        pOutputColl->GetCount(&count);
        for (UINT i = 0; i < count; ++i) {
            CComPtr<IMMDevice> pDevice;
            if (SUCCEEDED(pOutputColl->Item(i, &pDevice))) {
                // デバイス名を取得
                CComPtr<IPropertyStore> pProps;
                WCHAR nameBuffer[256] = L"Unknown Device";
                if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                    PROPVARIANT varName;
                    PropVariantInit(&varName);
                    if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                        if (varName.vt == VT_LPWSTR) {
                            wcscpy_s(nameBuffer, 256, varName.pwszVal);
                        }
                        PropVariantClear(&varName);
                    }
                }

                // デバイスIDを取得
                LPWSTR id = NULL;
                WCHAR idBuffer[512] = L"unknown-id";
                if (SUCCEEDED(pDevice->GetId(&id))) {
                    wcscpy_s(idBuffer, 512, id);
                    CoTaskMemFree(id);
                }

                // "devicename: deviceid" 形式の文字列を作成
                WCHAR result[768];
                swprintf_s(result, 768, L"%s: %s", nameBuffer, idBuffer);
                
                // Unicodeからchar*への変換
                char utf8Result[768 * 3];
                WideCharToMultiByte(CP_UTF8, 0, result, -1, utf8Result, sizeof(utf8Result), NULL, NULL);
                
                PyList_Append(device_list, PyUnicode_FromString(utf8Result));
            }
        }
    }

    CoUninitialize();
    return device_list;
}

// 詳細情報付きの出力（macOSの list_device_details に対応）
static PyObject* list_device_details(PyObject* self, PyObject* args) {
    PyObject* device_list = PyList_New(0);
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) return device_list;

    CComPtr<IMMDeviceEnumerator> pEnum;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL, IID_PPV_ARGS(&pEnum));
    if (FAILED(hr)) {
        CoUninitialize();
        return device_list;
    }

    // 入力デバイス（キャプチャ）を処理
    CComPtr<IMMDeviceCollection> pInputColl;
    hr = pEnum->EnumAudioEndpoints(eCapture, DEVICE_STATE_ACTIVE, &pInputColl);
    if (SUCCEEDED(hr)) {
        UINT count = 0;
        pInputColl->GetCount(&count);
        for (UINT i = 0; i < count; ++i) {
            CComPtr<IMMDevice> pDevice;
            if (SUCCEEDED(pInputColl->Item(i, &pDevice))) {
                PyObject *device_dict = PyDict_New();

                // デバイス名
                CComPtr<IPropertyStore> pProps;
                char nameBuffer[256] = "Unknown Device";
                if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                    PROPVARIANT varName;
                    PropVariantInit(&varName);
                    if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                        if (varName.vt == VT_LPWSTR) {
                            WideCharToMultiByte(CP_UTF8, 0, varName.pwszVal, -1, nameBuffer, sizeof(nameBuffer), NULL, NULL);
                        }
                        PropVariantClear(&varName);
                    }
                }

                // デバイスID（UID相当）
                LPWSTR id = NULL;
                char idBuffer[512] = "unknown-id";
                if (SUCCEEDED(pDevice->GetId(&id))) {
                    WideCharToMultiByte(CP_UTF8, 0, id, -1, idBuffer, sizeof(idBuffer), NULL, NULL);
                    CoTaskMemFree(id);
                }

                // メーカー名
                char manufacturerBuffer[256] = "Unknown";
                if (pProps) {
                    PROPVARIANT varManufacturer;
                    PropVariantInit(&varManufacturer);
                    if (SUCCEEDED(pProps->GetValue(PKEY_DeviceInterface_FriendlyName, &varManufacturer))) {
                        if (varManufacturer.vt == VT_LPWSTR) {
                            WideCharToMultiByte(CP_UTF8, 0, varManufacturer.pwszVal, -1, manufacturerBuffer, sizeof(manufacturerBuffer), NULL, NULL);
                        }
                        PropVariantClear(&varManufacturer);
                    }
                }

                // チャンネル数を取得
                UINT32 inputChannels = 0;
                UINT32 outputChannels = 0;
                CComPtr<IAudioClient> pAudioClient;
                if (SUCCEEDED(pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, NULL, (void**)&pAudioClient))) {
                    WAVEFORMATEX *pWfx = NULL;
                    if (SUCCEEDED(pAudioClient->GetMixFormat(&pWfx))) {
                        inputChannels = pWfx->nChannels;  // 入力デバイスなので入力チャンネル
                        CoTaskMemFree(pWfx);
                    }
                }

                // 辞書に値を設定
                PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
                PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(idBuffer));
                PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
                PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(inputChannels));
                PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(0)); // 入力デバイス
                PyDict_SetItemString(device_dict, "device_type", PyUnicode_FromString("input"));

                PyList_Append(device_list, device_dict);
                Py_DECREF(device_dict);
            }
        }
    }

    // 出力デバイス（レンダー）を処理
    CComPtr<IMMDeviceCollection> pOutputColl;
    hr = pEnum->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &pOutputColl);
    if (SUCCEEDED(hr)) {
        UINT count = 0;
        pOutputColl->GetCount(&count);
        for (UINT i = 0; i < count; ++i) {
            CComPtr<IMMDevice> pDevice;
            if (SUCCEEDED(pOutputColl->Item(i, &pDevice))) {
                PyObject *device_dict = PyDict_New();

                // デバイス名
                CComPtr<IPropertyStore> pProps;
                char nameBuffer[256] = "Unknown Device";
                if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                    PROPVARIANT varName;
                    PropVariantInit(&varName);
                    if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                        if (varName.vt == VT_LPWSTR) {
                            WideCharToMultiByte(CP_UTF8, 0, varName.pwszVal, -1, nameBuffer, sizeof(nameBuffer), NULL, NULL);
                        }
                        PropVariantClear(&varName);
                    }
                }

                // デバイスID（UID相当）
                LPWSTR id = NULL;
                char idBuffer[512] = "unknown-id";
                if (SUCCEEDED(pDevice->GetId(&id))) {
                    WideCharToMultiByte(CP_UTF8, 0, id, -1, idBuffer, sizeof(idBuffer), NULL, NULL);
                    CoTaskMemFree(id);
                }

                // メーカー名
                char manufacturerBuffer[256] = "Unknown";
                if (pProps) {
                    PROPVARIANT varManufacturer;
                    PropVariantInit(&varManufacturer);
                    if (SUCCEEDED(pProps->GetValue(PKEY_DeviceInterface_FriendlyName, &varManufacturer))) {
                        if (varManufacturer.vt == VT_LPWSTR) {
                            WideCharToMultiByte(CP_UTF8, 0, varManufacturer.pwszVal, -1, manufacturerBuffer, sizeof(manufacturerBuffer), NULL, NULL);
                        }
                        PropVariantClear(&varManufacturer);
                    }
                }

                // チャンネル数を取得
                UINT32 inputChannels = 0;
                UINT32 outputChannels = 0;
                CComPtr<IAudioClient> pAudioClient;
                if (SUCCEEDED(pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, NULL, (void**)&pAudioClient))) {
                    WAVEFORMATEX *pWfx = NULL;
                    if (SUCCEEDED(pAudioClient->GetMixFormat(&pWfx))) {
                        outputChannels = pWfx->nChannels;  // 出力デバイスなので出力チャンネル
                        CoTaskMemFree(pWfx);
                    }
                }

                // 辞書に値を設定
                PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
                PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(idBuffer));
                PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
                PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(0)); // 出力デバイス
                PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(outputChannels));
                PyDict_SetItemString(device_dict, "device_type", PyUnicode_FromString("output"));

                PyList_Append(device_list, device_dict);
                Py_DECREF(device_dict);
            }
        }
    }

    CoUninitialize();
    return device_list;
}

// デバイスタイプによるフィルタリング機能（macOSの list_devices_by_type に対応）
static PyObject* list_devices_by_type(PyObject* self, PyObject* args) {
    const char* device_type;
    if (!PyArg_ParseTuple(args, "s", &device_type)) {
        PyErr_SetString(PyExc_ValueError, "Device type parameter required: 'all', 'input', or 'output'");
        return NULL;
    }

    // パラメータの検証
    if (strcmp(device_type, "all") != 0 && 
        strcmp(device_type, "input") != 0 && 
        strcmp(device_type, "output") != 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid device type. Use 'all', 'input', or 'output'");
        return NULL;
    }

    PyObject* device_list = PyList_New(0);
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) return device_list;

    CComPtr<IMMDeviceEnumerator> pEnum;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL, IID_PPV_ARGS(&pEnum));
    if (FAILED(hr)) {
        CoUninitialize();
        return device_list;
    }

    // 入力デバイス（キャプチャ）を処理（"all" または "input" の場合）
    if (strcmp(device_type, "all") == 0 || strcmp(device_type, "input") == 0) {
        CComPtr<IMMDeviceCollection> pInputColl;
        hr = pEnum->EnumAudioEndpoints(eCapture, DEVICE_STATE_ACTIVE, &pInputColl);
        if (SUCCEEDED(hr)) {
            UINT count = 0;
            pInputColl->GetCount(&count);
            for (UINT i = 0; i < count; ++i) {
                CComPtr<IMMDevice> pDevice;
                if (SUCCEEDED(pInputColl->Item(i, &pDevice))) {
                    PyObject *device_dict = PyDict_New();

                    // デバイス名
                    CComPtr<IPropertyStore> pProps;
                    char nameBuffer[256] = "Unknown Device";
                    if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                        PROPVARIANT varName;
                        PropVariantInit(&varName);
                        if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                            if (varName.vt == VT_LPWSTR) {
                                WideCharToMultiByte(CP_UTF8, 0, varName.pwszVal, -1, nameBuffer, sizeof(nameBuffer), NULL, NULL);
                            }
                            PropVariantClear(&varName);
                        }
                    }

                    // デバイスID（UID相当）
                    LPWSTR id = NULL;
                    char idBuffer[512] = "unknown-id";
                    if (SUCCEEDED(pDevice->GetId(&id))) {
                        WideCharToMultiByte(CP_UTF8, 0, id, -1, idBuffer, sizeof(idBuffer), NULL, NULL);
                        CoTaskMemFree(id);
                    }

                    // メーカー名
                    char manufacturerBuffer[256] = "Unknown";
                    if (pProps) {
                        PROPVARIANT varManufacturer;
                        PropVariantInit(&varManufacturer);
                        if (SUCCEEDED(pProps->GetValue(PKEY_DeviceInterface_FriendlyName, &varManufacturer))) {
                            if (varManufacturer.vt == VT_LPWSTR) {
                                WideCharToMultiByte(CP_UTF8, 0, varManufacturer.pwszVal, -1, manufacturerBuffer, sizeof(manufacturerBuffer), NULL, NULL);
                            }
                            PropVariantClear(&varManufacturer);
                        }
                    }

                    // チャンネル数を取得
                    UINT32 inputChannels = 0;
                    CComPtr<IAudioClient> pAudioClient;
                    if (SUCCEEDED(pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, NULL, (void**)&pAudioClient))) {
                        WAVEFORMATEX *pWfx = NULL;
                        if (SUCCEEDED(pAudioClient->GetMixFormat(&pWfx))) {
                            inputChannels = pWfx->nChannels;
                            CoTaskMemFree(pWfx);
                        }
                    }

                    // 辞書に値を設定
                    PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
                    PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(idBuffer));
                    PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
                    PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(inputChannels));
                    PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(0));
                    PyDict_SetItemString(device_dict, "device_type", PyUnicode_FromString("input"));

                    PyList_Append(device_list, device_dict);
                    Py_DECREF(device_dict);
                }
            }
        }
    }

    // 出力デバイス（レンダー）を処理（"all" または "output" の場合）
    if (strcmp(device_type, "all") == 0 || strcmp(device_type, "output") == 0) {
        CComPtr<IMMDeviceCollection> pOutputColl;
        hr = pEnum->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &pOutputColl);
        if (SUCCEEDED(hr)) {
            UINT count = 0;
            pOutputColl->GetCount(&count);
            for (UINT i = 0; i < count; ++i) {
                CComPtr<IMMDevice> pDevice;
                if (SUCCEEDED(pOutputColl->Item(i, &pDevice))) {
                    PyObject *device_dict = PyDict_New();

                    // デバイス名
                    CComPtr<IPropertyStore> pProps;
                    char nameBuffer[256] = "Unknown Device";
                    if (SUCCEEDED(pDevice->OpenPropertyStore(STGM_READ, &pProps))) {
                        PROPVARIANT varName;
                        PropVariantInit(&varName);
                        if (SUCCEEDED(pProps->GetValue(PKEY_Device_FriendlyName, &varName))) {
                            if (varName.vt == VT_LPWSTR) {
                                WideCharToMultiByte(CP_UTF8, 0, varName.pwszVal, -1, nameBuffer, sizeof(nameBuffer), NULL, NULL);
                            }
                            PropVariantClear(&varName);
                        }
                    }

                    // デバイスID（UID相当）
                    LPWSTR id = NULL;
                    char idBuffer[512] = "unknown-id";
                    if (SUCCEEDED(pDevice->GetId(&id))) {
                        WideCharToMultiByte(CP_UTF8, 0, id, -1, idBuffer, sizeof(idBuffer), NULL, NULL);
                        CoTaskMemFree(id);
                    }

                    // メーカー名
                    char manufacturerBuffer[256] = "Unknown";
                    if (pProps) {
                        PROPVARIANT varManufacturer;
                        PropVariantInit(&varManufacturer);
                        if (SUCCEEDED(pProps->GetValue(PKEY_DeviceInterface_FriendlyName, &varManufacturer))) {
                            if (varManufacturer.vt == VT_LPWSTR) {
                                WideCharToMultiByte(CP_UTF8, 0, varManufacturer.pwszVal, -1, manufacturerBuffer, sizeof(manufacturerBuffer), NULL, NULL);
                            }
                            PropVariantClear(&varManufacturer);
                        }
                    }

                    // チャンネル数を取得
                    UINT32 outputChannels = 0;
                    CComPtr<IAudioClient> pAudioClient;
                    if (SUCCEEDED(pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, NULL, (void**)&pAudioClient))) {
                        WAVEFORMATEX *pWfx = NULL;
                        if (SUCCEEDED(pAudioClient->GetMixFormat(&pWfx))) {
                            outputChannels = pWfx->nChannels;
                            CoTaskMemFree(pWfx);
                        }
                    }

                    // 辞書に値を設定
                    PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
                    PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(idBuffer));
                    PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
                    PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(0));
                    PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(outputChannels));
                    PyDict_SetItemString(device_dict, "device_type", PyUnicode_FromString("output"));

                    PyList_Append(device_list, device_dict);
                    Py_DECREF(device_dict);
                }
            }
        }
    }

    CoUninitialize();
    return device_list;
}

static PyMethodDef methods[] = {
    {"list_device_uids", list_device_uids, METH_NOARGS, "List audio devices in 'name: id' format (Windows)"},
    {"list_device_details", list_device_details, METH_NOARGS, "List audio devices with detailed information (Windows)"},
    {"list_devices_by_type", list_devices_by_type, METH_VARARGS, "List audio devices filtered by type: 'all', 'input', or 'output' (Windows)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moddef = {
    PyModuleDef_HEAD_INIT, "_audio_devices", NULL, -1, methods
};

PyMODINIT_FUNC PyInit__audio_devices(void) {
    return PyModule_Create(&moddef);
}
