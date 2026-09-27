# Live Link setup after building

Build with Unreal Engine **5.8.3**, then follow these steps. Addresses in the screenshots belong to the original test session; use your phone's current address.

1. Open `MAP_M4_RadialMouth_POC`.

   ![Open the level](images/01-select-level.png)

2. Open **Window → Virtual Production → Live Link**.

   ![Open Live Link](images/02-open-live-link.png)

3. Add a **Live Link Face** source.

   ![Add source](images/03-add-source.png)

4. Keep Live Link Face open on a phone connected to the same network. Choose **MetaHuman Animator** capture mode and enable **Realtime Animation**.

   ![Phone setup](images/04-phone-setup.png)

5. Enter the phone address, port **14785**, and subject name **M4_iPhone**.

   ![Source settings](images/05-source-settings.png)

6. Connect and confirm a green subject indicator.

   ![Connected subject](images/06-connect.png)

7. Select the mouth actor in the Outliner. Enable **Use Live Link** and disable **Auto Oscillate**.

   ![Enable the actor input](images/07-enable-live-link.png)

8. Select **M4_iPhone** as the actor's Live Link Subject. Save the level **before Play**.

   ![Select the subject](images/08-select-subject.png)

9. Press Play and open/close your jaw. The center opening should expand/contract. **Live Link Status** on the Play actor shows the matched curve and value.

   ![Play the demo](images/09-play.png)

### Expected result

![Step X - Should ideally Workk](images/Step%20X%20-%20Should%20ideally%20Workk.gif)
