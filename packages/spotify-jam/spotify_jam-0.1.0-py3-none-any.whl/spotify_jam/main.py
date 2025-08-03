import requests

def startJam(authorizationToken: str) -> tuple[str, str]:
    """Starts a JAM on Spotify

    Args:
        authorizationToken (str): The Bearer token for your account used to create the JAM.

    Raises:
        Exception: When the status code of creating the session is not 200 OK

    Returns:
        tuple[str, str]: First is the JoinSessionURI, and the second is the SessionId
            JoinSessionURI: URI to the Spotify JAM. Ex "spotify:socialsession:2nntah4YWidehwLM4kxDyQ"
            SessionId: the id of the JAM used to end the JAM when desired
    """
    # current_or_new?activate=true
    # This itself does create the jam, it will also give us our join_session_token for creating a jam link!
    # Expecting a 200 OK from this request
    sessionCreationReq = requests.get("https://guc3-spclient.spotify.com/social-connect/v2/sessions/current_or_new?activate=true", headers={
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "app-platform": "Win32_x86_64",
        "authorization": authorizationToken,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.178 Spotify/1.2.69.449 Safari/537.36",
    })
    if sessionCreationReq.status_code != 200:
        raise Exception(f"Session Creation request did not result in a 200 OK status code. Status code returned: {sessionCreationReq.status_code}; Reason: {sessionCreationReq.reason}; Data: {sessionCreationReq.text}")
    sessionCreationResponseJson: dict = sessionCreationReq.json()
    #join_session_token = sessionCreationResponseJson["join_session_token"]
    joinSessionURI: str = sessionCreationResponseJson["join_session_uri"] # This link seems to work fine!
    sessionId: str = sessionCreationResponseJson["session_id"]
    
    return (joinSessionURI, sessionId)

def endJam(authorizationToken: str, sessionId: str) -> dict:
    """Ends a Spotify JAM

    Args:
        authorizationToken (str): The Bearer token for your account used to end the JAM.
        sessionId (str): The ID of the JAM, needed to end the JAM.

    Returns:
        dict:
            The "success" property is a bool telling you if the JAM was ended or not.
            The "request" property is the requests.Response from the delete request.
    """
    # Session ID is from the startJam
    # Expecting 200 OK from this request
    endJamReq = requests.delete(f"https://guc3-spclient.spotify.com/social-connect/v3/sessions/{sessionId}", headers={
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "app-platform": "Win32_x86_64",
        "authorization": authorizationToken,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.178 Spotify/1.2.69.449 Safari/537.36",
    })
    
    return {
        "success": endJamReq.status_code == 200, # 200 OK means we deleted it, else it failed
        "request": endJamReq # the entire request if people want to look at it to debug it.
    }

def getJamData(authorizationToken: str, sessionId: str) -> dict:
    """Returns the current state of the JAM

    Args:
        authorizationToken (str): The Bearer token for your account used to end the JAM.
        sessionId (str): The ID of the JAM, needed to end the JAM.

    Returns:
        dict:
        {
            "timestamp": str,
            "session_id": str,
            "join_session_token": str,
            "join_session_url": str,
            "session_owner_id": str,
            "session_members": [
                {
                    "joined_timestamp": str,
                    "id": str,
                    "username": str,
                    "display_name": str,
                    "image_url": str,
                    "large_image_url": str,
                    "is_listening": bool,
                    "is_controlling": bool,
                    "playbackControl": str,
                    "is_current_user": bool
                }
                ...
            ],
            "join_session_uri": str,
            "is_session_owner": bool,
            "is_listening": bool,
            "is_controlling": bool,
            "initialSessionType": str,
            "hostActiveDeviceId": str,
            "maxMemberCount": int,
            "active": bool,
            "queue_only_mode": bool,
            "wifi_broadcast": bool,
            "host_device_info": {
                "device_id": str,
                "output_device_info": {
                    "output_device_type": str,
                    "device_name": str
                },
                "device_name": str,
                "device_type": str,
                "is_group": bool
            }
        }
    """
    # The kick returns a full state of the jam, so if I kick nobody then we just get the current state
    return kickJamUser(authorizationToken, sessionId, "USER_ID") # A blank user id doesn't work, and no one will have this id

def kickJamUser(authorizationToken: str, sessionId: str, userId: str) -> dict:
    """Kicks the user with the specified ID from the JAM

    Args:
        authorizationToken (str): The Bearer token for your account used to end the JAM.
        sessionId (str): The ID of the JAM, needed to end the JAM.
        userId (str): The ID of the person you want to kick from the JAM.

    Raises:
        Exception: When the status code of creating the session is not 200 OK

    Returns:
        dict: Same return structure as getJamData
    """
    # I'm assuming that "28f163ba6ed4069bd7a8bf7031f2e6f9" is a userId but i need to check
    # Session ID is from the startJam. User ID is from 
    # Expecting 200 OK from this request
    kickRequest = requests.post(f"https://guc3-spclient.spotify.com/social-connect/v3/sessions/{sessionId}/member/{userId}/kick", headers={
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "app-platform": "Win32_x86_64",
        "authorization": authorizationToken,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.178 Spotify/1.2.69.449 Safari/537.36",
    })
    if kickRequest.status_code != 200:
        raise Exception(f"Kicking Jam User request did not result in a 200 OK status code. Note getJamData uses this function so that may be the problem. Status code returned: {kickRequest.status_code}; Reason: {kickRequest.reason}; Data: {kickRequest.text}")
    
    return kickRequest.json()

def allowJamUsersControlQueue(authorizationToken: str, allow: bool) -> bool:
    """Allows or disallows users to add stuff to the JAM queue

    Args:
        authorizationToken (str): The Bearer token for your account used to create the JAM.
        allow (bool): True to allow users to add to queue, and False to not allow them.

    Raises:
        Exception: When the status code of creating the session is not 200 OK.

    Returns:
        bool: True if it was successfully set.
    """
    URL = ""
    if allow == True: URL = "https://guc3-spclient.spotify.com/social-connect/v2/sessions/current/queue_only_mode/disabled"
    else: URL = "https://guc3-spclient.spotify.com/social-connect/v2/sessions/current/queue_only_mode/enabled"
    
    # Expecting 200 OK from this request
    usersQueueReq = requests.put(URL, headers={
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "app-platform": "Win32_x86_64",
        "authorization": authorizationToken,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.178 Spotify/1.2.69.449 Safari/537.36",
    })
    
    if usersQueueReq.status_code != 200:
        raise Exception(f"Kicking Jam User request did not result in a 200 OK status code. Note getJamData uses this function so that may be the problem. Status code returned: {usersQueueReq.status_code}; Reason: {usersQueueReq.reason}; Data: {usersQueueReq.text}")
    
    return True # if it failed it would've raised an exception

""" An unimplemented function that I don't want showing up right now
def allowJamUsersControlVolume(authorizationToken: str, allow: bool) -> bool:
    ""NOT IMPLEMENTED! I don't know if it is deprecated but I cannot find the option on my computer's app version nor on my Spotify mobile.
    Allows or disallows users to change the JAM volume.

    Args:
        authorizationToken (str): The Bearer token for your account used to end the JAM.
        allow (bool): True to allow users to control the volume, and False to not allow them.

    Raises:
        NotImplementedError: THIS FUNCTION IS NOT IMPLEMENTED YET

    Returns:
        bool: If the option was successful set or not
    ""
    # TODO: Add this feature. I don't know if it is deprecated but I cannot find the option on my computer's app version nor on my Spotify mobile.
    raise NotImplementedError("This function is not implemented yet! Try commit to the Github if you can figure it out!")
"""

