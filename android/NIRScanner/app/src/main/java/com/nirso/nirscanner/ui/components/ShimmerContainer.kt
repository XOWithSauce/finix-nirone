/*
 * This file is licensed under the Apache License 2.0. See the LICENSE file for details.
 */
package com.nirso.nirscanner.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun ShimmerContainer(
    modifier: Modifier,
    drawShimmer: Boolean = false,
    widthOfShadowBrush: Int = 300,
    angleOfAxisY: Float = 200f,
    durationMillis: Int = 3000,
    content: @Composable() () -> Unit
) {


    val shimmerColors = listOf(
        MaterialTheme.colorScheme.onSecondary.copy(alpha = 0.1f),
        MaterialTheme.colorScheme.scrim.copy(alpha = 0.04f),
        MaterialTheme.colorScheme.scrim.copy(alpha = 0.15f),
        MaterialTheme.colorScheme.scrim.copy(alpha = 0.04f),
        MaterialTheme.colorScheme.onSecondary.copy(alpha = 0.1f),
    )

    val transition = rememberInfiniteTransition(label = "")

    val translateAnimation = transition.animateFloat(
        initialValue = 0f,
        targetValue = (durationMillis + widthOfShadowBrush).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = durationMillis,
                easing = LinearEasing,
            ),
            repeatMode = RepeatMode.Restart,
        ),
        label = "Shimmer loading animation",
    )

    val brush = Brush.linearGradient(
        colors = shimmerColors,
        start = Offset(x = translateAnimation.value - widthOfShadowBrush, y = 0.0f),
        end = Offset(x = translateAnimation.value, y = angleOfAxisY),
    )

    Box(

        modifier = modifier
            .height(70.dp)
            .clip(shape = RoundedCornerShape(9.dp, 9.dp, 9.dp, 9.dp))
            .then(
                if (drawShimmer) {
                    Modifier.background(brush)
                } else {
                    Modifier.background(Color.Transparent)
                }
            )
        ,
    ) {
        content()
    }


}