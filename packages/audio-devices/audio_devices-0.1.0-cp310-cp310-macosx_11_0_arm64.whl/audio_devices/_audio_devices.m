// _audio_devices.m
#include <Python.h>
#include <CoreAudio/CoreAudio.h>
#include <AudioToolbox/AudioServices.h>

static PyObject* list_device_uids(PyObject* self, PyObject* args) {
    UInt32 propsize;
    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    };
    AudioObjectID *audioDevices;
    UInt32 deviceCount;

    AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &propsize);
    deviceCount = propsize / sizeof(AudioObjectID);
    audioDevices = malloc(propsize);
    AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &propsize, audioDevices);

    PyObject *device_list = PyList_New(0);
    for (UInt32 i = 0; i < deviceCount; ++i) {
        // デバイス名を取得
        CFStringRef deviceName = NULL;
        UInt32 nameSize = sizeof(deviceName);
        AudioObjectPropertyAddress prop_name = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        
        // デバイスUIDを取得
        CFStringRef uid = NULL;
        UInt32 uidSize = sizeof(uid);
        AudioObjectPropertyAddress prop_uid = {
            kAudioDevicePropertyDeviceUID,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        
        char nameBuffer[256] = "Unknown Device";
        char uidBuffer[256] = "unknown-uid";
        
        // デバイス名を取得
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_name, 0, NULL, &nameSize, &deviceName) == noErr && deviceName) {
            CFStringGetCString(deviceName, nameBuffer, sizeof(nameBuffer), kCFStringEncodingUTF8);
            CFRelease(deviceName);
        }
        
        // デバイスUIDを取得
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_uid, 0, NULL, &uidSize, &uid) == noErr && uid) {
            CFStringGetCString(uid, uidBuffer, sizeof(uidBuffer), kCFStringEncodingUTF8);
            CFRelease(uid);
        }
        
        // "devicename: deviceuid" 形式の文字列を作成
        char result[512];
        snprintf(result, sizeof(result), "%s: %s", nameBuffer, uidBuffer);
        PyList_Append(device_list, PyUnicode_FromString(result));
    }
    free(audioDevices);
    return device_list;
}

// typeパラメータで入力・出力デバイスを出し分けする関数
static PyObject* list_devices_by_type(PyObject* self, PyObject* args) {
    char *device_type = "all";  // デフォルトは全デバイス
    
    // 引数をパース（オプショナル）
    if (!PyArg_ParseTuple(args, "|s", &device_type)) {
        return NULL;
    }
    
    UInt32 propsize;
    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    };
    AudioObjectID *audioDevices;
    UInt32 deviceCount;

    AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &propsize);
    deviceCount = propsize / sizeof(AudioObjectID);
    audioDevices = malloc(propsize);
    AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &propsize, audioDevices);

    PyObject *device_list = PyList_New(0);
    for (UInt32 i = 0; i < deviceCount; ++i) {
        // 各種プロパティの取得
        CFStringRef deviceName = NULL;
        CFStringRef uid = NULL;
        CFStringRef manufacturer = NULL;
        UInt32 size;
        
        // デバイス名
        char nameBuffer[256] = "Unknown Device";
        AudioObjectPropertyAddress prop_name = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(deviceName);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_name, 0, NULL, &size, &deviceName) == noErr && deviceName) {
            CFStringGetCString(deviceName, nameBuffer, sizeof(nameBuffer), kCFStringEncodingUTF8);
            CFRelease(deviceName);
        }
        
        // デバイスUID
        char uidBuffer[256] = "unknown-uid";
        AudioObjectPropertyAddress prop_uid = {
            kAudioDevicePropertyDeviceUID,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(uid);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_uid, 0, NULL, &size, &uid) == noErr && uid) {
            CFStringGetCString(uid, uidBuffer, sizeof(uidBuffer), kCFStringEncodingUTF8);
            CFRelease(uid);
        }
        
        // メーカー名
        char manufacturerBuffer[256] = "Unknown";
        AudioObjectPropertyAddress prop_manufacturer = {
            kAudioDevicePropertyDeviceManufacturerCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(manufacturer);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_manufacturer, 0, NULL, &size, &manufacturer) == noErr && manufacturer) {
            CFStringGetCString(manufacturer, manufacturerBuffer, sizeof(manufacturerBuffer), kCFStringEncodingUTF8);
            CFRelease(manufacturer);
        }
        
        // 入力チャンネル数
        UInt32 inputChannels = 0;
        AudioObjectPropertyAddress prop_input_streams = {
            kAudioDevicePropertyStreamConfiguration,
            kAudioDevicePropertyScopeInput,
            kAudioObjectPropertyElementMaster
        };
        if (AudioObjectGetPropertyDataSize(audioDevices[i], &prop_input_streams, 0, NULL, &size) == noErr) {
            AudioBufferList *bufferList = malloc(size);
            if (AudioObjectGetPropertyData(audioDevices[i], &prop_input_streams, 0, NULL, &size, bufferList) == noErr) {
                for (UInt32 j = 0; j < bufferList->mNumberBuffers; ++j) {
                    inputChannels += bufferList->mBuffers[j].mNumberChannels;
                }
            }
            free(bufferList);
        }
        
        // 出力チャンネル数
        UInt32 outputChannels = 0;
        AudioObjectPropertyAddress prop_output_streams = {
            kAudioDevicePropertyStreamConfiguration,
            kAudioDevicePropertyScopeOutput,
            kAudioObjectPropertyElementMaster
        };
        if (AudioObjectGetPropertyDataSize(audioDevices[i], &prop_output_streams, 0, NULL, &size) == noErr) {
            AudioBufferList *bufferList = malloc(size);
            if (AudioObjectGetPropertyData(audioDevices[i], &prop_output_streams, 0, NULL, &size, bufferList) == noErr) {
                for (UInt32 j = 0; j < bufferList->mNumberBuffers; ++j) {
                    outputChannels += bufferList->mBuffers[j].mNumberChannels;
                }
            }
            free(bufferList);
        }
        
        // typeパラメータに基づいてフィルタリング
        bool include_device = false;
        if (strcmp(device_type, "all") == 0) {
            include_device = true;
        } else if (strcmp(device_type, "input") == 0) {
            include_device = (inputChannels > 0);
        } else if (strcmp(device_type, "output") == 0) {
            include_device = (outputChannels > 0);
        }
        
        if (include_device) {
            // Python辞書を作成
            PyObject *device_dict = PyDict_New();
            PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
            PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(uidBuffer));
            PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
            PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(inputChannels));
            PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(outputChannels));
            PyDict_SetItemString(device_dict, "device_id", PyLong_FromUnsignedLong(audioDevices[i]));
            
            // デバイスタイプを決定
            const char *type_string = "unknown";
            if (inputChannels > 0 && outputChannels > 0) {
                type_string = "both";
            } else if (inputChannels > 0) {
                type_string = "input";
            } else if (outputChannels > 0) {
                type_string = "output";
            }
            PyDict_SetItemString(device_dict, "device_type", PyUnicode_FromString(type_string));
            
            PyList_Append(device_list, device_dict);
            Py_DECREF(device_dict);
        }
    }
    free(audioDevices);
    return device_list;
}

// より詳細な情報を含む拡張版（参考）
static PyObject* list_device_details(PyObject* self, PyObject* args) {
    UInt32 propsize;
    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    };
    AudioObjectID *audioDevices;
    UInt32 deviceCount;

    AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &propsize);
    deviceCount = propsize / sizeof(AudioObjectID);
    audioDevices = malloc(propsize);
    AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &propsize, audioDevices);

    PyObject *device_list = PyList_New(0);
    for (UInt32 i = 0; i < deviceCount; ++i) {
        // 各種プロパティの取得
        CFStringRef deviceName = NULL;
        CFStringRef uid = NULL;
        CFStringRef manufacturer = NULL;
        UInt32 size;
        
        // デバイス名
        char nameBuffer[256] = "Unknown Device";
        AudioObjectPropertyAddress prop_name = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(deviceName);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_name, 0, NULL, &size, &deviceName) == noErr && deviceName) {
            CFStringGetCString(deviceName, nameBuffer, sizeof(nameBuffer), kCFStringEncodingUTF8);
            CFRelease(deviceName);
        }
        
        // デバイスUID
        char uidBuffer[256] = "unknown-uid";
        AudioObjectPropertyAddress prop_uid = {
            kAudioDevicePropertyDeviceUID,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(uid);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_uid, 0, NULL, &size, &uid) == noErr && uid) {
            CFStringGetCString(uid, uidBuffer, sizeof(uidBuffer), kCFStringEncodingUTF8);
            CFRelease(uid);
        }
        
        // メーカー名
        char manufacturerBuffer[256] = "Unknown";
        AudioObjectPropertyAddress prop_manufacturer = {
            kAudioDevicePropertyDeviceManufacturerCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster
        };
        size = sizeof(manufacturer);
        if (AudioObjectGetPropertyData(audioDevices[i], &prop_manufacturer, 0, NULL, &size, &manufacturer) == noErr && manufacturer) {
            CFStringGetCString(manufacturer, manufacturerBuffer, sizeof(manufacturerBuffer), kCFStringEncodingUTF8);
            CFRelease(manufacturer);
        }
        
        // 入力チャンネル数
        UInt32 inputChannels = 0;
        AudioObjectPropertyAddress prop_input_streams = {
            kAudioDevicePropertyStreamConfiguration,
            kAudioDevicePropertyScopeInput,
            kAudioObjectPropertyElementMaster
        };
        if (AudioObjectGetPropertyDataSize(audioDevices[i], &prop_input_streams, 0, NULL, &size) == noErr) {
            AudioBufferList *bufferList = malloc(size);
            if (AudioObjectGetPropertyData(audioDevices[i], &prop_input_streams, 0, NULL, &size, bufferList) == noErr) {
                for (UInt32 j = 0; j < bufferList->mNumberBuffers; ++j) {
                    inputChannels += bufferList->mBuffers[j].mNumberChannels;
                }
            }
            free(bufferList);
        }
        
        // 出力チャンネル数
        UInt32 outputChannels = 0;
        AudioObjectPropertyAddress prop_output_streams = {
            kAudioDevicePropertyStreamConfiguration,
            kAudioDevicePropertyScopeOutput,
            kAudioObjectPropertyElementMaster
        };
        if (AudioObjectGetPropertyDataSize(audioDevices[i], &prop_output_streams, 0, NULL, &size) == noErr) {
            AudioBufferList *bufferList = malloc(size);
            if (AudioObjectGetPropertyData(audioDevices[i], &prop_output_streams, 0, NULL, &size, bufferList) == noErr) {
                for (UInt32 j = 0; j < bufferList->mNumberBuffers; ++j) {
                    outputChannels += bufferList->mBuffers[j].mNumberChannels;
                }
            }
            free(bufferList);
        }
        
        // Python辞書を作成
        PyObject *device_dict = PyDict_New();
        PyDict_SetItemString(device_dict, "name", PyUnicode_FromString(nameBuffer));
        PyDict_SetItemString(device_dict, "uid", PyUnicode_FromString(uidBuffer));
        PyDict_SetItemString(device_dict, "manufacturer", PyUnicode_FromString(manufacturerBuffer));
        PyDict_SetItemString(device_dict, "input_channels", PyLong_FromUnsignedLong(inputChannels));
        PyDict_SetItemString(device_dict, "output_channels", PyLong_FromUnsignedLong(outputChannels));
        PyDict_SetItemString(device_dict, "device_id", PyLong_FromUnsignedLong(audioDevices[i]));
        
        PyList_Append(device_list, device_dict);
        Py_DECREF(device_dict);
    }
    free(audioDevices);
    return device_list;
}

// メソッド定義を更新
static PyMethodDef methods[] = {
    {"list_device_uids", list_device_uids, METH_NOARGS, "List audio devices in 'name: uid' format (macOS)"},
    {"list_device_details", list_device_details, METH_NOARGS, "List audio devices with detailed information (macOS)"},
    {"list_devices_by_type", list_devices_by_type, METH_VARARGS, "List audio devices filtered by type: 'all', 'input', or 'output' (macOS)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moddef = {
    PyModuleDef_HEAD_INIT, "_audio_devices", NULL, -1, methods
};

PyMODINIT_FUNC PyInit__audio_devices(void) {
    return PyModule_Create(&moddef);
}
