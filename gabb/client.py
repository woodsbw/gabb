# Ignoring several pylint methods for now:
#   unused-argument: There is processing of arguments going on via locals()
#       that pylint isn't catching
#   too-many-arguments, too-many-public-methods: Given the functionality of
#       this package, the choice was made to just represent the APIs as they
#       exist, which means a large number of methods and attributes.
# pylint: disable=unused-argument, too-many-arguments, too-many-public-methods
"""API client for Gabb.

This contains the GabbClient class, which serves as the main REST API client 
    for the services used by the Gabb (https://gabb.com) smartwatch/smartphone 
    for children. While the devices are made by Gabb, they utilize the FiLIP 
    service provided by Smartcom (https://smartcom.com) to manage the data and 
    devices and that is what the class connects to.

Example:
    client = GabbClient("username", "password")
    client.get_contacts()
"""
import datetime
from urllib.parse import urljoin
import requests
from gabb.session import GabbSession


class GabbClient:
    """Gabb REST API Python Client

    This class serves as the main REST API client for the services used by the
    Gabb (https://gabb.com) smartwatch/smartphone for children. While the
    devices are made by Gabb, they utilize the FiLIP service provided by
    Smartcom (https://smartcom.com) to manage the data and devices and that is
    what the class connects to.
    """

    _required_headers = {
        "X-Accept-Language": "en-US",
        "X-Accept-Offset": "-5.000000",
        "Accept-Version": "1.0",
        "User-Agent": "FiLIP-iOS",
        "X-Accept-Version": "1.0",
        "Content-Type": "application/json",
    }
    """dict: A dict of static headers that the API requires in order to function 
    properly"""

    def __init__(
        self, username: str, password: str, base_url: str = "https://api.myfilip.com/"
    ) -> None:
        """Initializes object and sets up API access

        This exists primarily to do the initial API authentication and store
        the required tokens to support later use.

        Args:
            username (str): Parent/guardian account username.
            password (str): Parent/guardian account password.
            base_url (str, optional): The API base URL. Base URL is without the
                v2, as safezones doesn't use it

        Example:
            client = GabbClient("example@example.com", "password")
        """
        base_url_v2 = urljoin(base_url, "v2/")

        # Setup the session. We use the "v2" version for the base_url as primary
        # because it is used by nearly all the endpoints
        self._session = GabbSession(
            username=username,
            password=password,
            base_url=base_url_v2,
            alt_base_url=base_url,
        )
        """The session that will be used for communication with the URL"""

        self._session.headers.update(self._required_headers)

    def get_contacts(self) -> requests.Response:
        """Get account contacts

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_contacts()
        """
        return self._session.get("contact")

    def add_contact(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        relationship: str,
        devices: list,
        photo: str = "",
        emgergency: bool = False,
        enable_chat_school_mode: bool = False,
        guest: bool = False,
        guest_primary_access: bool = False,
    ) -> requests.Response:
        """Add contact to account

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Args:
            first_name (str): First name of contact.
            last_name: (str): Last name of contact
            phone (str): Phone number of contact (in full international format)
            relationship (str): Relationship with device owner
            devices (list[int]): Devices to apply contact to.
            photo (str): It is technically possible to upload a photo as a
                string, but no work has been done to figure out the encoding,
                so do at your own risk.
            emgergency (bool, optional): If this user should be
            enable_chat_school_mode (bool, optional):
            guest (bool, optional):
            guest_primary_access (bool, optional):

        Example:
            resp = client.add_contact(
                phone="+15555555555",
                first_name="Bill",
                last_name="Smith",
                relationship="Friend",
                devices=[555555],
            )
        """

        payload = {
            "phone": phone,
            "guest": guest,
            "firstName": first_name,
            "enableChatSchoolMode": enable_chat_school_mode,
            "emergency": emgergency,
            "relationship": relationship,
            "photo": photo,
            "devices": devices,
            "guestPrimaryAccess": guest_primary_access,
            "lastName": last_name,
        }

        return self._session.post("contact", json=payload)

    def delete_contact(self, contact_id: int) -> requests.Response:
        """Delete contact

        Args:
            contact_id (str): ID number of the contact to delete. Can retrieve
                from the get_contact method.

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_contact(5555555)
        """
        return self._session.delete(f"contact/{contact_id}")

    def get_emergency_contact(self) -> requests.Response:
        """Get the identity of the emergency contacts for all devices on the account

        Examples:
            resp = client.get_emergency_contact()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.
        """
        return self._session.get("contact/emergency")

    def set_emergency_contact(self, device_id, contact_id) -> requests.Response:
        """Set the identity of the emergency contact

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            contact_id (int): The ID of of the constact to set as emergency. Can
                be gotten from get_contacts()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.set_emergency_contact(
                device_id=555555,
                contact_id=5555555
            )
        """
        payload = {"contactId": contact_id, "isTemplate": False}

        return self._session.put(f"contact/emergency/{device_id}", json=payload)

    def get_device_profile(self, device_id: int) -> requests.Response:
        """Get the device profile

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_device_profile(555555)
        """
        return self._session.get(f"device/profile/{device_id}")

    def update_device_profile(
        self,
        device_id: int,
        gender: int = None,
        first_name: str = None,
        last_name: str = None,
        birth_date: datetime.datetime = None,
    ) -> requests.Response:
        """Update device profile, which is the mainly info about the child using
        the device

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            gender (int): Gender of the child, int 1 for male and int 2 for female
            firstName (str): First name of the child
            lastName (str): Last name of the child
            birthDate (datetime.datetime): Birthdate of the child as a datetime object

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            birthday = datetime.datetime(2015, 5, 5, 5, 0, 0)
            resp = client.update_device_profile(
                device_id=555555,
                birthDate=birthday,
                gender=2
            )
        """
        payload = GabbClient.prepare_params_for_api_call(
            locals_=locals(), values_to_filter=["device_id"]
        )

        if "birthDate" in payload:
            payload["birthDate"] = round(
                payload["birthDate"].replace(tzinfo=datetime.timezone.utc).timestamp()
                * 1000
            )

        return self._session.put(f"device/update-profile/{device_id}", json=payload)

    def get_map(self) -> requests.Response:
        """Get device geolocation data, as well as a general device info

        Example:
            resp = client.get_map()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.
        """
        return self._session.get("map")

    def refresh_map(self, device_id: int) -> requests.Response:
        """Refresh device geolocation data

        Example:
            resp = client.refresh_map(555555)

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.
        """
        return self._session.post(f"map/refresh/{device_id}")

    def get_event_log(self) -> requests.Response:
        """Get the entries in the event log

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_event_log()
        """
        return self._session.get("eventlogs")

    def delete_event_log(self) -> requests.Response:
        """Delete ALL events in the event log

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_event_log()
        """
        return self._session.delete("eventlogs")

    def get_event_log_count(self) -> requests.Response:
        """Get a count of current number events in the log

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_event_log_count()
        """
        return self._session.get("eventlogs/count")

    def get_device_settings(self, device_id: int) -> requests.Response:
        """Get device settings

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.update_device_settings(
                device_id=555555, silent_mode=False, active_tracking_enable=False
            )
        """
        return self._session.get(f"settings/{device_id}")

    def update_device_settings(
        self,
        device_id: int,
        active_tracking_enable: bool = None,
        active_tracking_duration: int = None,
        active_tracking_frequency: int = None,
        battery_power_saving_mode: bool = None,
        tracking_enabled: bool = None,
        tracking_start_time: datetime.time = None,
        tracking_end_time: datetime.time = None,
        tracking_interval: int = None,
        silent_mode: bool = None,
    ) -> requests.Response:
        """Update settings for a device

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            active_tracking_enable (bool): Enable active tracking at the active
                (faster, but more battery intensive) tracking interval
            active_tracking_duration (int): How long active (lower interval/higher
                battery usage) tracking should continue after being enabled, in seconds
            active_tracking_frequency (int): Active (faster, but more battery
                intensive) tracking interval in seconds
            battery_power_saving_mode (bool): Enable/disable battery saving mode
            tracking_enabled (bool): Enable/disable tracking
            tracking_start_time (datetime.time): Time of day to start tracking (daily)
            tracking_end_time (datetime.time): Time of day to end tracking (daily)
            tracking_interval (int): Standard tracking interval (how often the device
                sends location data) in seconds.
            silent_mode (bool): Enable/disable silent mode for the device

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            tracking_start_time = datetime.time(0,0,0)
            tracking_end_time = datetime.time(23,59,59)

            resp = client.update_device_settings(
                device_id=555555,
                tracking_enabled=True,
                tracking_start_time=tracking_start_time,
                tracking_end_time=tracking_end_time,
                tracking_interval=900
            )

        todo:
            Make the time stuff actually work
        """
        locals_ = locals()

        locals_["tracking_start_time"] = str(tracking_start_time)[:-3]
        locals_["tracking_end_time"] = str(tracking_end_time)[:-3]

        filtered_locals = GabbClient.prepare_params_for_api_call(locals_, ["device_id"])

        # print(filtered_locals)

        return self._session.put(f"settings/{device_id}", json=filtered_locals)

    def get_user_profile(self) -> requests.Response:
        """Get the user (parent) profile

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.
        """
        return self._session.get("user/profile")

    def get_goals(self, device_id: int) -> requests.Response:
        """Get the goals set for a specific device. Step goal is the only one
        used by Gabb

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_goals(555555)
        """
        return self._session.get(f"device/goals/{device_id}")

    def set_step_goal(self, device_id: int, step_goal: int) -> requests.Response:
        """Set the step goal for a specific device.

        Only step goal is exposed, as it is all Gabb is using and setting the
        others may have unexpected results.

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            step_goal (int): Goal for steps in a day

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.set_step_goal(device_id=555555, step_goal=10000)
        """
        filtered_locals = GabbClient.prepare_params_for_api_call(
            locals(), ["device_id"]
        )

        return self._session.post(f"device/goals/{device_id}", json=filtered_locals)

    def get_lock_mode_schedules(self) -> requests.Response:
        """Get lock mode schedules

        Gabb seems to actually make use of an API on the FiLIP API service here
        that is intended for alarms, which results in unexpected calls. But,
        the settings represented here are used for lock mode schedules.

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_lock_mode_schedules()
        """
        return self._session.get("alarms")

    def create_lock_mode_schedule(
        self,
        week_days: list[bool],
        name: str,
        devices: list[int],
        time: datetime.time,
        end_time: datetime.time,
        enabled: bool,
    ) -> requests.Response:
        """Set a lock mode schedule

        Gabb seems to actually make use of an API on the FiLIP API service here
        that is intended for alarms, which results in unexpected calls. But,
        the settings represented here are used for lock mode schedules.

        Args:
            week_days (list[bool]): Days of the week that the lock mode schedule
                should be active, represented as an array of seven boolean values,
                where each value represents a day of the week, in the format:
                [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday].
                So, a lock mode schedule active only on weekdays would be:
                [True, True, True, True, True, False, False]
            name (str): A name for the lock mode schedule.
            devices (list[int]): A list of device IDs for the lock mode schedule
                to apply to
            time (datetime.time): Time for the lock mode to begin on each active
                day
            end_time:(datetime.time): Time for the lock mode to end on each
                active day
            enabled (bool): Enabled/disabled state of the lock mode schedule

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.create_lock_mode_schedule(
                week_days=[True, False, True, False, True, False, True],
                name="AName123456",
                devices=[555555],
                time=datetime.time(hour=3, minute=15, second=30),
                end_time=datetime.time(hour=7, minute=15, second=30),
                enabled=True,
            )
        """
        locals_ = locals()

        unused_defaults_to_add = {
            "silent_mode": False,
            "type": 4,
            "date": None,
            "school_mode": True,
            "focus_mode": False,
        }

        locals_["time"] = GabbClient.convert_time_to_seconds(time)

        locals_["end_time"] = GabbClient.convert_time_to_seconds(end_time)

        locals_.update(unused_defaults_to_add)

        payload = GabbClient.prepare_params_for_api_call(
            locals_=locals_, title_case=True
        )

        return self._session.post("alarms", json=payload)

    def delete_lock_mode_schedule(
        self, lock_mode_schedule_id: int
    ) -> requests.Response:
        """Delete lock mode schedule

        Gabb seems to actually make use of an API on the FiLIP API service here
        that is intended for alarms, which results in unexpected calls. But,
        the settings represented here are used for lock mode schedules.

        Args:
            lock_mode_schedule_id (int): The ID of the lock mode schedule from
                get_lock_mode_schedule()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_lock_mode_schedule(555555)
        """
        return self._session.delete(f"alarms/{lock_mode_schedule_id}")

    def update_lock_mode_schedule(
        self,
        lock_mode_schedule_id: int,
        week_days: list[bool] = None,
        name: str = None,
        devices: list[int] = None,
        time: datetime.time = None,
        end_time: datetime.time = None,
        enabled: bool = None,
    ) -> requests.Response:
        """Set a lock mode schedule

        Gabb seems to actually make use of an API on the FiLIP API service here
        that is intended for alarms, which results in unexpected calls. But,
        the settings represented here are used for lock mode schedules.

        Args:
            lock_mode_schedule_id (int): The ID of the lock mode schedule from
                get_lock_mode_schedule()
            week_days (list[bool]): Days of the week that the lock mode schedule
                should be active, represented as an array of seven boolean values,
                where each value represents a day of the week, in the format:
                [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday].
                So, a lock mode schedule active only on weekdays would be:
                [True, True, True, True, True, False, False]
            name (str): A name for the lock mode schedule.
            devices (list[int]): A list of device IDs for the lock mode schedule
                to apply to
            time (datetime.time): Time for the lock mode to begin on each active
                day
            end_time:(datetime.time): Time for the lock mode to end on each
                active day
            enabled (bool): Enabled/disabled state of the lock mode schedule

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.update_lock_mode_schedule(
                lock_mode_schedule_id (int): 555555,
                week_days=[True, False, True, False, True, False, True],
                name="AName123456",
                devices=[555555],
                time=datetime.time(hour=3, minute=15, second=30),
                end_time=datetime.time(hour=7, minute=15, second=30),
                enabled=True,
            )
        """
        locals_ = locals()

        unused_defaults_to_add = {
            "silent_mode": False,
            "type": 4,
            "date": None,
            "school_mode": True,
            "focus_mode": False,
        }

        locals_["time"] = GabbClient.convert_time_to_seconds(time)

        locals_["end_time"] = GabbClient.convert_time_to_seconds(end_time)

        locals_.update(unused_defaults_to_add)

        payload = GabbClient.prepare_params_for_api_call(
            locals_=locals_, title_case=True, values_to_filter=["lock_mode_schedule_id"]
        )

        return self._session.put(f"alarms/{lock_mode_schedule_id}", json=payload)

    def get_todos(self) -> requests.Response:
        """Get todos

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_todos()
        """
        return self._session.get("todo")

    def delete_todo(self, device_id: int, todo_id: int) -> requests.Response:
        """Delete todo

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            todo_id (int): Todo ID to delete, from get_todos()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_todo(device_id=555555, todo_id=555555)
        """
        payload = GabbClient.prepare_params_for_api_call(locals_=locals())

        return self._session.delete("todo", json=payload)

    def add_todo(self) -> requests.Response:
        """Adding todos not yet implemented, as the data structure isn't yet fully
        understood

        Raises:
            NotImplementedError: Raised on any call to this method until implemented
        """
        raise NotImplementedError("Adding Todos not yet supported.")

    def update_todo(self) -> requests.Response:
        """Updating todos not yet implemented, as the data structure isn't yet fully
        understood

        Raises:
            NotImplementedError: Raised on any call to this method until implemented
        """
        raise NotImplementedError("Updating Todos not yet supported")

    def get_text_presets(self, device_id: int) -> requests.Response:
        """Get text preset options for a device

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_text_presets()
        """
        return self._session.get(f"tokk/device/{device_id}/preset")

    def delete_text_preset(self, device_id: int, preset_id: int) -> requests.Response:
        """Delete text preset option

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            preset_id (int): Text preset ID, from get_text_presets()

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_text_preset(device_id=555555, preset_id=55555555)

        """
        return self._session.delete(f"tokk/device/{device_id}/preset/{preset_id}")

    def add_text_preset(self, device_id: int, message: str) -> requests.Response:
        """Create text preset for a device

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            message (str): The text of the text preset message

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.add_text_preset(
                device_id=555555,
                message="This is a text preset message"
            )
        """
        payload = GabbClient.prepare_params_for_api_call(locals_=locals())

        return self._session.post(f"tokk/device/{device_id}/preset", json=payload)

    def update_text_preset(
        self, device_id: int, preset_id: int, message: str
    ) -> requests.Response:
        """Update an existing text preset message

        Args:
            device_id (int): Device ID of the device to set the emergency contact
                for. Device ID is easiest to get from get_map()
            preset_id (int): Text preset ID, from get_text_presets()
            message (str): The text of the text preset message

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.update_text_preset(
                device_id=555555,
                present_id=55555555,
                message="This is a text preset message"
            )
        """
        payload = GabbClient.prepare_params_for_api_call(locals_=locals())

        return self._session.put(
            f"tokk/device/{device_id}/preset/{preset_id}",
            json=payload,
        )

    def get_safezones(self) -> requests.Response:
        """Get the safezones for the account

        The safezones API is very different from everything else, both in
        technical implementation and in objects returned. Main thing to be
        aware of for use is that attributes in the JSON response come back in
        TitleCase instead of camelCase.

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.get_safezones()
        """
        self._session.use_alt_base_url_next_request = True
        return self._session.get("safezone/list")

    def add_safezone(
        self,
        longitude: float,
        latitude: float,
        name: str,
        radius: float,
        enabled: bool,
        devices: list[int],
    ) -> requests.Response:
        """Add a safezone to the account

        The safezones API is very different from everything else, both in
        technical implementation and in objects returned. Main thing to be
        aware of for use is that attributes in the JSON response come back in
        TitleCase instead of camelCase.

        Args:
            longitude (float): Longitude for the safezone location
            latitude (float): Latitude for the safezone location
            name (str): A name for the safezone
            radius (float): An allowed radius for the safezone from the lat/long
                point...I think in feet? The minimum the app will establish is
                around 150. Not sure what the maximum would be.
            enabled (bool): If safezone is enabled/disabled
            devices (list[int]): A list of device IDs that this safezone should
                be applied to

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.add_safezone(
                longitude=-80.48236483894243,
                latitude=48.51629188103274,
                name="An Safezone Test",
                radius="150.0",
                enabled=True,
                devices=[555555],
            )
        """
        payload = GabbClient.prepare_params_for_api_call(
            locals_=locals(), title_case=True
        )

        self._session.use_alt_base_url_next_request = True

        return self._session.post("safezone/add", json=payload)

    def delete_safezone(self, zone_id: str) -> requests.Response:
        """Delete a safezone

        Args:
            zone_id (int): The safezone ID to delete (from get_safezones())

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.delete_safezone(555555)
        """
        self._session.use_alt_base_url_next_request = True
        return self._session.post(f"safezone/delete?zoneId={zone_id}")

    def update_safezone(
        self,
        zone_id: str,
        longitude: float,
        latitude: float,
        name: str,
        radius: float,
        enabled: bool,
        devices: list[int],
    ) -> requests.Response:
        """Update a safezone to the account

        The safezones API is very different from everything else, both in
        technical implementation and in objects returned. Main thing to be
        aware of for use is that attributes in the JSON response come back in
        TitleCase instead of camelCase.

        Args:
            zone_id (int): The safezone ID to delete (from get_safezones())
            longitude (float): Longitude for the safezone location
            latitude (float): Latitude for the safezone location
            name (str): A name for the safezone
            radius (float): An allowed radius for the safezone from the lat/long
                point...I think in feet? The minimum the app will establish is
                around 150. Not sure what the maximum would be.
            enabled (bool): If safezone is enabled/disabled
            devices (list[int]): A list of device IDs that this safezone should
                be applied to

        Returns:
            requests.Response: The raw response object (per the requests
                library) for the API response.

        Example:
            resp = client.add_safezone(
                zone_id=555555,
                longitude=-80.48236483894243,
                latitude=48.51629188103274,
                name="An Safezone Test",
                radius="150.0",
                enabled=True,
                devices=[555555],
            )
        """
        payload = GabbClient.prepare_params_for_api_call(
            locals_=locals(), values_to_filter=["zone_id"], title_case=True
        )

        self._session.use_alt_base_url_next_request = True

        return self._session.post(f"safezone/edit?zoneId={zone_id}", json=payload)

    @staticmethod
    def convert_time_to_seconds(time: datetime.time) -> int:
        """A static method to take a datetime.time and convert it into seconds
        into a day

        Args:
            time (datetime.time): A time object for the time of day

        Returns:
            int: The number of seconds into the day for the input time

        Example:
            time_to_use = datetime.time(5,0,0)
            GabbClient.convert_time_to_seconds(time_to_us)
        """
        return int(
            datetime.timedelta(
                hours=time.hour, minutes=time.minute, seconds=time.second
            ).total_seconds()
        )

    @staticmethod
    def prepare_params_for_api_call(
        locals_: dict, values_to_filter: list = None, title_case: bool = False
    ) -> dict:
        """Take the return value of locals() from an API method in this class
        and prepare them

        This method will strip out values that don't need to be passed to the
        API (self, plus any caller defined exclusions, or params with a value
        of None), change the param names from snake_case to either camelCase
        or TitleCase.

        Args:
            locals_ (dict): Params to work on, normally the return value of a
                call to locals() within the calling method
            values_to_filter (list): A list of keys to filter out of locals_
                and exclude from the returned dict
            title_case (bool): If we should use TitleCase. If False, camelCase
                will be used.

        Returns:
            dict: The filtered and formatted params to pass to the API

        Example:
            def add_object(
                self,
                device_id: int,
                first_name: str,
                last_name: str,
                relationship: str
                ):
                payload = GabbClient.prepare_params_for_api_call(
                    locals_=locals(),
                    values_to_filter=['device_id']
                )

                resp = requests.post(
                    "https://api.server.net/v2/object/{device_id}".format(device_id),
                    json=payload
                )
        """
        if values_to_filter is None:
            values_to_filter = []
        values_to_filter.append("self")
        filtered_locals = {}

        for key, value in locals_.items():
            if value is not None and key not in values_to_filter:
                if title_case:
                    new_key = key.title().replace("_", "")
                else:
                    new_key = key[0] + key.title().replace("_", "")[1:]
                filtered_locals[new_key] = value

        return filtered_locals
