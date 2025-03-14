/*
 * Copyright 2023 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.nirso.nirscanner.ble

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.graphics.drawable.shapes.RoundRectShape
import android.os.Build
import android.os.ParcelUuid
import android.util.Log
import androidx.annotation.RequiresApi
import androidx.annotation.RequiresPermission
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.getSystemService
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.LifecycleOwner
import com.nirso.nirscanner.ble.server.GATTServerSampleService.Companion.SERVICE_UUID
import com.nirso.nirscanner.ui.components.ShimmerContainer
import com.nirso.nirscanner.ui.components.SnackbarManager
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@SuppressLint("MissingPermission")
@RequiresApi(Build.VERSION_CODES.M)
@Composable
fun FindBLEDevicesSample() {
    BluetoothSampleBox {
        FindDevicesScreen {
            Log.d("FindDeviceSample", "Name: ${it.name} Address: ${it.address} Type: ${it.type}")
        }
    }
}

@SuppressLint("InlinedApi", "MissingPermission")
@RequiresApi(Build.VERSION_CODES.M)
@RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
@Composable
internal fun FindDevicesScreen(onConnect: (BluetoothDevice) -> Unit) {
    val context = LocalContext.current
    val adapter = checkNotNull(context.getSystemService<BluetoothManager>()?.adapter)
    val scope = rememberCoroutineScope()
    var scanning by remember {
        mutableStateOf(true)
    }
    val devices = remember {
        mutableStateMapOf<BluetoothDevice, Int>()
    }

    val sampleServerDevices = remember {
        mutableStateListOf<BluetoothDevice>()
    }
    val scanSettings: ScanSettings = ScanSettings.Builder()
        .setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
        .setScanMode(ScanSettings.SCAN_MODE_BALANCED)
        .build()

    // This effect will start scanning for devices when the screen is visible
    // If scanning is stop removing the effect will stop the scanning.
    if (scanning) {
        BluetoothScanEffect(
            scanSettings = scanSettings,
            onScanFailed = {
                scanning = false
                scope.launch {
                    SnackbarManager.snackbarHostState.showSnackbar(
                        message = "FindBLEDevicesSample: Scan failed with error: $it",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onDeviceFound = { scanResult ->
                if (!devices.contains(scanResult.device)) {
                    if (scanResult.rssi >= -55) {
                        devices.put(scanResult.device, scanResult.rssi)
                    }
                }

                // If we find our GATT server sample let's highlight it
                val serviceUuids = scanResult.scanRecord?.serviceUuids.orEmpty()
                if (serviceUuids.contains(ParcelUuid(SERVICE_UUID))) {
                    if (!sampleServerDevices.contains(scanResult.device)) {
                        sampleServerDevices.add(scanResult.device)
                    }
                }
            },
        )
        // Stop scanning after a while
        LaunchedEffect(true) {
            delay(15000)
            scanning = false
        }
    }

    Column(Modifier.fillMaxSize()) {
        Row(
            Modifier
                .fillMaxWidth()
                .height(54.dp)
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Available devices",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.inversePrimary
            )
            if (scanning) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.scrim)
            } else {
                IconButton(
                    onClick = {
                        devices.clear()
                        scanning = true
                    },
                ) {
                    Icon(
                        imageVector = Icons.Rounded.Refresh,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.scrim
                    )
                }
            }
        }

        LazyColumn(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (devices.isEmpty()) {
                item {
                    Text(text = "No devices found")
                }
            }
            val deviceList = devices.map { entry -> entry.key }
            items(deviceList) { item ->
                val rssi = devices.getValue(item)
                BluetoothDeviceItem(
                    bluetoothDevice = item,
                    isSampleServer = sampleServerDevices.contains(item),
                    onConnect = onConnect,
                    rssi = rssi,
                )
            }
        }
    }
}

@SuppressLint("MissingPermission")
@Composable
internal fun BluetoothDeviceItem(
    bluetoothDevice: BluetoothDevice,
    isSampleServer: Boolean = false,
    onConnect: (BluetoothDevice) -> Unit,
    rssi: Int = 0,
) {
    ShimmerContainer(modifier = Modifier.fillMaxSize(), drawShimmer = (isSampleServer)) {
        Row(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth()
                .clickable { onConnect(bluetoothDevice) }
                .then(
                    if (isSampleServer) {
                        Modifier.border( // Apply border only if isSampleServer is true
                            width = 2.dp,
                            color = MaterialTheme.colorScheme.scrim,
                            shape = RoundedCornerShape(8.dp)
                        )
                    } else {
                        // Do something with modifier
                        Modifier.border( // Apply border only if isSampleServer is true
                            width = 2.dp,
                            color = MaterialTheme.colorScheme.inverseSurface,
                            shape = RoundedCornerShape(8.dp)
                        )
                    }
                ),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                if (isSampleServer) {
                    bluetoothDevice.name ?: "NIR Device"
                } else {
                    bluetoothDevice.name ?: "N/A"
                },
                style = if (isSampleServer) {
                    TextStyle(fontWeight = FontWeight.Bold)
                } else {
                    TextStyle(fontWeight = FontWeight.Normal)
                },
                color = MaterialTheme.colorScheme.inversePrimary,
                modifier = Modifier
                    .padding(8.dp, 0.dp, 0.dp, 0.dp),
            )
            Text(text = "RSSI: $rssi")
            Text(
                text = bluetoothDevice.address,
                modifier = Modifier
                    .padding(0.dp, 0.dp, 8.dp, 0.dp),
            )
        }
    }
}

@SuppressLint("InlinedApi")
@RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
@Composable
private fun BluetoothScanEffect(
    scanSettings: ScanSettings,
    lifecycleOwner: LifecycleOwner = LocalLifecycleOwner.current,
    onScanFailed: (Int) -> Unit,
    onDeviceFound: (device: ScanResult) -> Unit,
) {
    val context = LocalContext.current
    val adapter = context.getSystemService<BluetoothManager>()?.adapter

    if (adapter == null) {
        onScanFailed(ScanCallback.SCAN_FAILED_INTERNAL_ERROR)
        return
    }

    val currentOnDeviceFound by rememberUpdatedState(onDeviceFound)

    DisposableEffect(lifecycleOwner, scanSettings) {
        val leScanCallback: ScanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                super.onScanResult(callbackType, result)
                currentOnDeviceFound(result)
            }

            override fun onScanFailed(errorCode: Int) {
                super.onScanFailed(errorCode)
                onScanFailed(errorCode)
            }
        }

        val observer = LifecycleEventObserver { _, event ->
            // Start scanning once the app is in foreground and stop when in background
            if (event == Lifecycle.Event.ON_START) {
                adapter.bluetoothLeScanner.startScan(null, scanSettings, leScanCallback)
            } else if (event == Lifecycle.Event.ON_STOP) {
                adapter.bluetoothLeScanner.stopScan(leScanCallback)
            }
        }

        // Add the observer to the lifecycle
        lifecycleOwner.lifecycle.addObserver(observer)

        // When the effect leaves the Composition, remove the observer and stop scanning
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            adapter.bluetoothLeScanner.stopScan(leScanCallback)
        }
    }
}
