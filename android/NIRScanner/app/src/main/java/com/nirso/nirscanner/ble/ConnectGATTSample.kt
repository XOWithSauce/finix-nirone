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
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattService
import android.bluetooth.BluetoothProfile
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresApi
import androidx.annotation.RequiresPermission
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Build
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ElevatedButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.focusModifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.LifecycleOwner
import com.nirso.nirscanner.R
import com.nirso.nirscanner.ble.server.GATTServerSampleService.Companion.CHARACTERISTIC_UUID
import com.nirso.nirscanner.ble.server.GATTServerSampleService.Companion.SERVICE_UUID
import com.nirso.nirscanner.ui.components.SnackbarManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import com.nirso.nirscanner.auth.AuthManager
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

@OptIn(ExperimentalAnimationApi::class)
@SuppressLint("MissingPermission")
@RequiresApi(Build.VERSION_CODES.M)
@Composable
fun ConnectGATTSample() {
    var selectedDevice by remember {
        mutableStateOf<BluetoothDevice?>(null)
    }
    // Check that BT permissions and that BT is available and enabled
    BluetoothSampleBox {
        AnimatedContent(targetState = selectedDevice, label = "Selected device") { device ->
            if (device == null) {
                // Scans for BT devices and handles clicks (see FindDeviceSample)
                FindDevicesScreen {
                    selectedDevice = it
                }
            } else {
                // Once a device is selected show the UI and try to connect device
                ConnectDeviceScreen(device = device) {
                    selectedDevice = null
                }
            }
        }
    }
}

private data class DeviceConnectionState(
    val gatt: BluetoothGatt?,
    val connectionState: Int = 0,
    val mtu: Int,
    val services: List<BluetoothGattService> = emptyList(),
    val servicesDiscovered: Boolean = false,
    val messageSent: Boolean = false,
    val messageReceived: String = "",
    var sensorTemp: String = "0",        // polledAction 1
    var sensorCalibrated: String = "False",  // polledAction 2
    var predictedFabrics: String = "",  // polledAction 3
    var polledAction: Int = 0
) {
    companion object {
        val None = DeviceConnectionState(null, -1, -1)
    }
}

data class PollAction(val actionId: Int, val command: String)

fun pollData(intervalMillis: Long = 20000): Flow<Unit> = flow {
    while (true) {
        emit(Unit)
        delay(intervalMillis)
    }
}

@SuppressLint("InlinedApi")
@RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
@Composable
fun ConnectDeviceScreen(device: BluetoothDevice, onClose: () -> Unit) {
    val scope = rememberCoroutineScope()

    // Keeps track of the last connection state with the device
    var state by remember {
        mutableStateOf<DeviceConnectionState>(DeviceConnectionState.None)
    }
    // Once the device services are discovered find the GATTServerSample service
    val service by remember(state?.services) {
        mutableStateOf(state?.services?.find { it.uuid == SERVICE_UUID })
    }
    // If the GATTServerSample service is found, get the characteristic
    val characteristic by remember(service) {
        mutableStateOf(service?.getCharacteristic(CHARACTERISTIC_UUID))
    }

    var expanded by remember { mutableStateOf(false) }

    var newMessage by remember { mutableStateOf("") }
    val authManager = remember { AuthManager() }

    // This effect will handle the connection and notify when the state changes
    BLEConnectEffect(device = device, authManager) {
        // update our state to recompose the UI
        state = it
    }

    // This effect will poll device statistics
    LaunchedEffect(key1 = state?.servicesDiscovered) {

        if (state?.gatt != null && characteristic != null) {
            var i = 0
            while(true) {
                
                // Main task is to poll the prediction labels and percentages (probability of being label textile type)
                delay(3000)
                state?.polledAction = 3
                scope.launch(Dispatchers.IO) {
                    // Poll prediction labels
                    sendData(state?.gatt!!, characteristic!!, "poll_Label", authManager)
                    delay(1000) // Wait for response
                    state!!.gatt?.readCharacteristic(characteristic)
                }


                // If sensor is not calibrated, we poll for its calibration status
                if (state?.sensorCalibrated == "False") {
                    delay(3000)
                    state?.polledAction = 2
                    scope.launch(Dispatchers.IO) {
                        // Poll calibration status
                        sendData(state?.gatt!!, characteristic!!, "b_Calibrated", authManager)
                        delay(1000) // Wait for response
                        state!!.gatt?.readCharacteristic(characteristic)
                    }
                }

                i++

                // Every fifth iteration we check serial temperature 
                if (i == 5) {
                    delay(3000)
                    state?.polledAction = 1
                    scope.launch(Dispatchers.IO) {
                        // Poll calibration status
                        sendData(state?.gatt!!, characteristic!!, "i_Sertemp", authManager)
                        delay(1000) // Wait for response
                        state!!.gatt?.readCharacteristic(characteristic)
                    }
                    i = 0
                }

            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row {
            Column {
                Text(
                    text = device.name ?: "Name not resolved",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.inversePrimary,
                )
                Text(text = device.address)
            }
            Spacer(Modifier.weight(1f))
            Icon(
                painter = painterResource(
                    id = if (state?.connectionState == BluetoothProfile.STATE_CONNECTED) {
                        R.drawable.edgesensor_high_green
                    } else {
                        R.drawable.edgesensor_high_red
                    }
                ),
                contentDescription = null,
                tint = Color.Unspecified,
                modifier = Modifier
                    .size(53.dp),
            )
        }
        Row {
            Text(text = "Calibrated", style = MaterialTheme.typography.titleLarge)
            Icon(
                imageVector = if(state?.sensorCalibrated == "True") {
                    Icons.Rounded.Check
                } else {
                    Icons.Rounded.Close
                },
                contentDescription = null,
                tint = if(state?.sensorCalibrated == "True") {
                    MaterialTheme.colorScheme.inverseOnSurface
                } else {
                    MaterialTheme.colorScheme.errorContainer
                },
                modifier = Modifier
                    .padding(10.dp, 0.dp, 0.dp, 0.dp),
            )
        }
        Text(text = "Sensor Temperature: ${state?.sensorTemp} ℃", style = MaterialTheme.typography.titleLarge)
        Divider(
            modifier = Modifier
                .padding(0.dp, 6.dp, 0.dp, 6.dp),
            color = MaterialTheme.colorScheme.scrim.copy(alpha = 1f),
            thickness = 3.dp,
        )
        Text(
            modifier = Modifier.fillMaxWidth(),
            text = "${state?.predictedFabrics}",
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.titleLarge,
            color = MaterialTheme.colorScheme.onSurface
        )
        Divider(
            modifier = Modifier
                .padding(0.dp, 6.dp, 0.dp, 6.dp),
            color = MaterialTheme.colorScheme.scrim.copy(alpha = 1f),
            thickness = 3.dp,
        )
        if(state?.sensorCalibrated != "True") {
            ElevatedButton(
                enabled = state?.gatt != null && characteristic != null,
                modifier = Modifier
                    .padding(0.dp, 0.dp),
                onClick = {
                    scope.launch(Dispatchers.IO) {
                        sendData(state?.gatt!!,
                            characteristic!!,
                            "m_Whiteref",
                            authManager)
                    }
                },
                border = BorderStroke(1.dp, color = MaterialTheme.colorScheme.scrim),
                contentPadding = PaddingValues(
                    start = 30.dp,
                    top = 10.dp,
                    end = 30.dp,
                    bottom = 10.dp
                ),
                elevation = ButtonDefaults.elevatedButtonElevation(
                    defaultElevation = 5.dp,
                    pressedElevation = 2.dp,
                    focusedElevation = 5.dp,
                    hoveredElevation = 5.dp,
                    disabledElevation = 2.dp
                )
            ) {
                Text(
                    color = MaterialTheme.colorScheme.inversePrimary,
                    letterSpacing = 2.sp,
                    fontSize = 16.sp,
                    text = "White Reference"
                )
            }

            ElevatedButton(
                enabled = state?.gatt != null && characteristic != null,
                modifier = Modifier
                    .padding(0.dp, 0.dp),
                onClick = {
                    scope.launch(Dispatchers.IO) {
                        sendData(state?.gatt!!,
                            characteristic!!,
                            "m_Darkref",
                            authManager)
                    }
                },
                border = BorderStroke(1.dp, color = MaterialTheme.colorScheme.scrim),
                contentPadding = PaddingValues(
                    start = 30.dp,
                    top = 10.dp,
                    end = 30.dp,
                    bottom = 10.dp
                ),
                elevation = ButtonDefaults.elevatedButtonElevation(
                    defaultElevation = 5.dp,
                    pressedElevation = 2.dp,
                    focusedElevation = 5.dp,
                    hoveredElevation = 5.dp,
                    disabledElevation = 2.dp
                )
            ) {
                Text(
                    color = MaterialTheme.colorScheme.inversePrimary,
                    letterSpacing = 2.sp,
                    fontSize = 16.sp,
                    text = "Dark Reference"
                )
            }
        }


        Box() {
            Row() {
                Button(
                    onClick = { expanded = true },
                ) {
                    Icon(
                        Icons.Rounded.Build,
                        contentDescription = "Devtools",
                        tint = MaterialTheme.colorScheme.scrim.copy(alpha = 1f),
                        modifier = Modifier
                            .size(20.dp)
                            .padding(0.dp)
                    )
                    Text(
                        text = "Open Dev Tools",
                        fontSize = 12.sp,
                        modifier = Modifier
                            .padding(12.dp, 0.dp, 10.dp, 0.dp)
                    )

                }
            }
            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false },
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight()
                    .padding(12.dp, 12.dp, 12.dp, 12.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(0.dp, 12.dp, 0.dp, 12.dp),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(
                        onClick = { expanded = false },
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.errorContainer),
                        shape = RoundedCornerShape(50),
                    ) {
                        Text(text = "Close", fontSize = 25.sp)
                        Icon(
                            Icons.Rounded.Close,
                            contentDescription = "Devtools",
                            tint = MaterialTheme.colorScheme.errorContainer,
                            modifier = Modifier
                                .size(40.dp)
                        )
                    }
                }
                Text(
                    text = "Message sent: ${state?.messageSent}",
                    modifier = Modifier.padding(0.dp, 0.dp, 0.dp, 6.dp)
                )
                Text(
                    text = "Message received: ${state?.messageReceived}",
                    modifier = Modifier.padding(0.dp, 6.dp, 0.dp, 12.dp)
                )
                OutlinedTextField(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(0.dp, 5.dp, 0.dp, 5.dp),
                    value = newMessage,
                    onValueChange = { newMessage = it },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = MaterialTheme.colorScheme.outline,
                        unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                    )
                )
                Button(
                    enabled = state?.gatt != null && characteristic != null,
                    onClick = {
                        scope.launch(Dispatchers.IO) {
                            sendData(state?.gatt!!, characteristic!!, newMessage, authManager)
                        }
                    },
                ) {
                    Text(text = "Write to server")
                }

                Button(
                    enabled = state?.gatt != null && characteristic != null,
                    onClick = {
                        scope.launch(Dispatchers.IO) {
                            state?.gatt?.readCharacteristic(characteristic)
                        }
                    },
                ) {
                    Text(text = "Read characteristic")
                }
            }
        }

        Button(onClick = onClose) {
            Text(text = "Close")
        }
    }
}

/**
 * Writes "hello world" to the server characteristic
 */
@RequiresApi(Build.VERSION_CODES.O)
@SuppressLint("MissingPermission")
suspend fun sendData(
    gatt: BluetoothGatt,
    characteristic: BluetoothGattCharacteristic,
    newMessage: String,
    authManager: AuthManager
) {
    val jsonString = authManager.encryptMessage(newMessage)
    val data = jsonString.toByteArray()
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        gatt.writeCharacteristic(
            characteristic,
            data,
            BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT,
        )
    } else {
        characteristic.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
        @Suppress("DEPRECATION")
        characteristic.value = data
        @Suppress("DEPRECATION")
        gatt.writeCharacteristic(characteristic)
    }
}

internal fun Int.toConnectionStateString() = when (this) {
    BluetoothProfile.STATE_CONNECTED -> "Connected"
    BluetoothProfile.STATE_CONNECTING -> "Connecting"
    BluetoothProfile.STATE_DISCONNECTED -> "Disconnected"
    BluetoothProfile.STATE_DISCONNECTING -> "Disconnecting"
    else -> "N/A"
}

@SuppressLint("InlinedApi", "MissingPermission")
@RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
@Composable
private fun BLEConnectEffect(
    device: BluetoothDevice,
    authManager: AuthManager,
    lifecycleOwner: LifecycleOwner = LocalLifecycleOwner.current,
    onStateChange: (DeviceConnectionState) -> Unit,
) {
    val context = LocalContext.current
    val currentOnStateChange by rememberUpdatedState(onStateChange)

    // Keep the current connection state
    var state by remember {
        mutableStateOf(DeviceConnectionState.None)
    }
    val scope = rememberCoroutineScope()

    DisposableEffect(lifecycleOwner, device) {
        // This callback will notify us when things change in the GATT connection so we can update
        // our state
        val callback = object : BluetoothGattCallback() {
            override fun onConnectionStateChange(
                gatt: BluetoothGatt,
                status: Int,
                newState: Int,
            ) {
                super.onConnectionStateChange(gatt, status, newState)
                state = state.copy(gatt = gatt, connectionState = newState)
                currentOnStateChange(state)
                if (status != BluetoothGatt.GATT_SUCCESS) {
                    // Here you should handle the error returned in status based on the constants
                    // https://developer.android.com/reference/android/bluetooth/BluetoothGatt#summary
                    // For example for GATT_INSUFFICIENT_ENCRYPTION or
                    // GATT_INSUFFICIENT_AUTHENTICATION you should create a bond.
                    // https://developer.android.com/reference/android/bluetooth/BluetoothDevice#createBond()
                    scope.launch {
                        SnackbarManager.snackbarHostState.showSnackbar(
                            message = "BLEConnectEffect: An error happened: $status",
                            duration = SnackbarDuration.Short
                        )
                    }
                }
                scope.launch {
                    // If Connected
                    if (state.connectionState == 2) {
                        SnackbarManager.snackbarHostState.showSnackbar(
                            message = "Successfully connected!",
                            duration = SnackbarDuration.Short
                        )
                        if(state.gatt != null) {
                            // Request mtu
                            gatt.requestMtu(23)
                            // Auto discover services
                            gatt.discoverServices()
                        }

                    }

                }

            }

            override fun onMtuChanged(gatt: BluetoothGatt, mtu: Int, status: Int) {
                super.onMtuChanged(gatt, mtu, status)
                state = state.copy(gatt = gatt, mtu = mtu)
                currentOnStateChange(state)
            }

            override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
                super.onServicesDiscovered(gatt, status)
                state = state.copy(services = gatt.services)
                scope.launch {
                    SnackbarManager.snackbarHostState.showSnackbar(
                        message = "Services discovered!",
                        duration = SnackbarDuration.Short
                    )
                }
                state = state.copy(servicesDiscovered = true)
                currentOnStateChange(state)
            }

            override fun onCharacteristicWrite(
                gatt: BluetoothGatt?,
                characteristic: BluetoothGattCharacteristic?,
                status: Int,
            ) {
                super.onCharacteristicWrite(gatt, characteristic, status)
                state = state.copy(messageSent = status == BluetoothGatt.GATT_SUCCESS)
                currentOnStateChange(state)
            }

            @Suppress("DEPRECATION", "OVERRIDE_DEPRECATION")
            override fun onCharacteristicRead(
                gatt: BluetoothGatt,
                characteristic: BluetoothGattCharacteristic,
                status: Int,
            ) {
                super.onCharacteristicRead(gatt, characteristic, status)
                if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
                    doOnRead(characteristic.value)
                }
            }

            override fun onCharacteristicRead(
                gatt: BluetoothGatt,
                characteristic: BluetoothGattCharacteristic,
                value: ByteArray,
                status: Int,
            ) {
                super.onCharacteristicRead(gatt, characteristic, value, status)
                doOnRead(value)
            }

            private fun doOnRead(value: ByteArray) {
                val decodedMessage = authManager.decryptMessage(value.decodeToString(), scope)
                state = state.copy(messageReceived = decodedMessage)
                if (state.polledAction == 1)
                    state = state.copy(sensorTemp = decodedMessage)
                if (state.polledAction == 2)
                    state = state.copy(sensorCalibrated = decodedMessage)
                if (state.polledAction == 3)
                    state = state.copy(predictedFabrics = decodedMessage)


                currentOnStateChange(state)
            }

        }

        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_START) {
                if (state.gatt != null) {
                    // If we previously had a GATT connection let's reestablish it
                    state.gatt?.connect()
                } else {
                    // Otherwise create a new GATT connection
                    state = state.copy(gatt = device.connectGatt(context, false, callback))
                }
            } else if (event == Lifecycle.Event.ON_STOP) {
                // Unless you have a reason to keep connected while in the bg you should disconnect
                state.gatt?.disconnect()
            }
        }

        // Add the observer to the lifecycle
        lifecycleOwner.lifecycle.addObserver(observer)

        // When the effect leaves the Composition, remove the observer and close the connection
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            state.gatt?.close()
            state = DeviceConnectionState.None
        }

    }
}
