import threading
import time
from core.api_client import AgeSmartApiClient
from utilities.media_helper import MediaStandardizationService, ImagePrivacyProcessor, get_video_duration, get_iphone_profile

class WorkflowEvent:
    STARTED = "verification.request.accepted"
    UPLOAD_STARTED = "verification.document.upload.started"
    UPLOAD_SUCCESS = "verification.document.upload.success"
    UPLOAD_FAILED = "verification.document.upload.failed"
    POLLING_STARTED = "verification.status.polling.started"
    FINISHED = "verification.request.finished"

class SmartVerificationWorkflow:
    def __init__(self, auth_service=None, telemetry_service=None, api_client=None, smartweb_service=None):
        self.auth = auth_service
        self.telemetry = telemetry_service
        self.api_client = api_client or AgeSmartApiClient()
        self.smartweb_service = smartweb_service
        self.is_running = False
        self.callbacks = []

    def on_event(self, callback):
        self.callbacks.append(callback)

    def trigger(self, event_name, data=None):
        for cb in self.callbacks:
            cb(event_name, data)

    def start_workflow(self, document_path, selfie_path, video_path, token="DUMMY_TOKEN", dob="2000-01-01", timecodes=""):
        if self.is_running:
            return
            
        self.is_running = True
        threading.Thread(
            target=self._run_workflow_async,
            args=(document_path, selfie_path, video_path, token, dob, timecodes),
            daemon=True
        ).start()

    def _run_workflow_async(self, doc_path, selfie_path, video_path, token, dob, timecodes):
        try:
            # 0. Select unified iPhone Camera Profile (iPhone 13 - 18)
            iphone_profile = get_iphone_profile()
            self.trigger(WorkflowEvent.STARTED, f"Camera Profile: Apple {iphone_profile['model']} ({iphone_profile['software']})")
            
            # Synchronize User-Agent on api_client to match the iPhone profile
            ios_ver = iphone_profile["software"].replace("iOS ", "").strip()
            os_ver_score = ios_ver.replace(".", "_")
            iphone_ua = f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_ver_score} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ios_ver} Mobile/15E148 Safari/604.1"
            self.api_client.set_user_agent(iphone_ua)
            
            self.trigger(WorkflowEvent.STARTED, "Initializing workflow and fetching CSRF...")
            if not self.api_client.initialize_session(token):
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": "Failed to initialize session (CSRF load)."})
                return

            # --- 1. Document Processing (Standardize & Inject iPhone Back Camera EXIF) ---
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Standardizing Document to Apple {iphone_profile['model']} JPEG...")
            std_doc, doc_converted = MediaStandardizationService.standardize_image(doc_path, profile=iphone_profile, is_selfie=False)
            if doc_converted:
                self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Document standardized with {iphone_profile['lens_back']} metadata.")
                
            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Processing & uploading Document (Original)...")
            doc_original = ImagePrivacyProcessor.sanitize_image_metadata(std_doc, "original_doc", profile=iphone_profile, is_selfie=False)
            res_doc1 = self.api_client.upload_image(doc_original, "FRONT_ID_ORIGINAL", token)
            if not res_doc1["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_doc1.get("error")})
                return
            
            time.sleep(2)
            
            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Processing & uploading Document (Altered)...")
            doc_altered = ImagePrivacyProcessor.create_altered_image(std_doc, profile=iphone_profile, is_selfie=False)
            res_doc2 = self.api_client.upload_image(doc_altered, "FRONT_ID_ALTERED", token)
            if not res_doc2["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_doc2.get("error")})
                return
            
            time.sleep(2)

            # --- 2. Selfie Processing (Standardize & Inject iPhone Front Camera EXIF) ---
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Standardizing Selfie to Apple {iphone_profile['model']} JPEG...")
            std_selfie, selfie_converted = MediaStandardizationService.standardize_image(selfie_path, profile=iphone_profile, is_selfie=True)
            if selfie_converted:
                self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Selfie standardized with {iphone_profile['lens_front']} metadata.")

            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Processing & uploading Selfie (Original)...")
            selfie_original = ImagePrivacyProcessor.sanitize_image_metadata(std_selfie, "original_selfie", profile=iphone_profile, is_selfie=True)
            res_selfie1 = self.api_client.upload_image(selfie_original, "SELFIE_ORIGINAL", token)
            if not res_selfie1["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_selfie1.get("error")})
                return
                
            time.sleep(2)
            
            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Processing & uploading Selfie (Altered)...")
            selfie_altered = ImagePrivacyProcessor.create_altered_image(std_selfie, profile=iphone_profile, is_selfie=True)
            res_selfie2 = self.api_client.upload_image(selfie_altered, "SELFIE_ALTERED", token)
            if not res_selfie2["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_selfie2.get("error")})
                return
                
            time.sleep(2)

            # --- 3. Video Processing (ffprobe Probe & ffmpeg iPhone QuickTime/MP4 Metadata) ---
            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Probing video stream with ffprobe...")
            probe = MediaStandardizationService.probe_video(video_path)
            probe_desc = f"{probe.get('format_name', 'video')}/{probe.get('codec_name', 'unknown')}"
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"ffprobe: {probe_desc}, duration={probe.get('duration', 0.0):.1f}s")
            
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Standardizing video to Apple {iphone_profile['model']} MP4 (H.264/AAC)...")
            std_video, vid_converted = MediaStandardizationService.standardize_video(
                video_path,
                profile=iphone_profile,
                log_callback=lambda m: self.trigger(WorkflowEvent.UPLOAD_STARTED, f"FFmpeg: {m}")
            )
            
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Injecting Apple {iphone_profile['model']} QuickTime metadata with ffmpeg...")
            video_sanitized = ImagePrivacyProcessor.sanitize_video_metadata(std_video, "video", profile=iphone_profile)
            duration = probe.get("duration") or get_video_duration(video_sanitized)
            
            self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Uploading Video ({duration:.1f}s)...")
            res_vid = self.api_client.upload_video(video_sanitized, token, duration)
            if not res_vid["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_vid.get("error")})
                return
                
            # Submit final sequences
            self.trigger(WorkflowEvent.UPLOAD_STARTED, "Performing final submit sequence (this takes time)...")
            def log_cb(msg):
                self.trigger(WorkflowEvent.UPLOAD_STARTED, f"Submit Sequence: {msg}")
                
            doc_hash = res_doc1["file_name"]
            selfie_hash = res_selfie1["file_name"]
            vid_hash = res_vid["file_name"]
            
            res_final = self.api_client.submit_final(token, dob, doc_hash, selfie_hash, vid_hash, timecodes, log_callback=log_cb)
            if not res_final["success"]:
                self.trigger(WorkflowEvent.FINISHED, {"status": "Error", "error": res_final.get("error")})
                return

            self.trigger(WorkflowEvent.POLLING_STARTED, "Polling verification status...")
            for attempt in range(1, 31):
                time.sleep(3) # Polling interval
                status = self.api_client.get_verification_status(token)
                self.trigger(WorkflowEvent.POLLING_STARTED, f"Poll {attempt}: Status = {status}")
                if status and status.upper() in ["APPROVED", "REJECTED", "ERROR"]:
                    result_payload = {"status": status}
                    if self.smartweb_service:
                        ok, msg = self.smartweb_service.submit_result(token, status)
                        result_payload["website_synced"] = ok
                        result_payload["website_msg"] = msg
                    self.trigger(WorkflowEvent.FINISHED, result_payload)
                    if self.telemetry:
                        self.telemetry.log_event(f"Workflow Finished: {status}")
                    return
                    
            result_payload = {"status": "Timeout", "error": "Polling timed out after 30 attempts."}
            if self.smartweb_service:
                self.smartweb_service.submit_result(token, "FAILED")
            self.trigger(WorkflowEvent.FINISHED, result_payload)
            
        except Exception as e:
            result_payload = {"status": "Exception", "error": str(e)}
            if self.smartweb_service:
                try:
                    self.smartweb_service.submit_result(token, "FAILED")
                except:
                    pass
            self.trigger(WorkflowEvent.FINISHED, result_payload)
            if self.telemetry:
                self.telemetry.log_event(f"Workflow Exception: {e}")
        finally:
            self.is_running = False
