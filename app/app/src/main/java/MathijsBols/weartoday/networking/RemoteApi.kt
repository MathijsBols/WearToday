package MathijsBols.weartoday.networking

import java.io.BufferedReader
import java.io.InputStream
import java.net.HttpURLConnection
import java.io.InputStreamReader
import java.net.URL
import android.util.Log


class RemoteApi {

    val BASE_URL = "https://PUT CUSTOM HERE"
    fun getRooster(callback: (String) -> Unit){
        Thread(Runnable {

            val connection = URL(BASE_URL).openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.setRequestProperty("Content-Type","application/json")
            connection.setRequestProperty("Accept","application/json")
            connection.setRequestProperty("Authorization", "Bearer PUT CUSTOM HERE")
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.doInput = true

            try{
                val reader = InputStreamReader(connection.inputStream)

                reader.use { input ->

                    val response= StringBuilder()
                    val bufferedReader = BufferedReader(input)

                    bufferedReader.forEachLine {
                        response.append(it.trim())
                    }

                    callback(response.toString())
                }
            }catch (e : Exception){
                callback(e.localizedMessage)
            }
            connection.disconnect()


        }).start()
    }
}