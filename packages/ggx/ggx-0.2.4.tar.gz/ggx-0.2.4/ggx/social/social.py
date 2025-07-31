from ..client.game_client import GameClient
from loguru import logger





class Social(GameClient):
    
    
    
    
    async def send_player_sms(
        self,
        player_name: str,
        sms_title: str,
        sms_text: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sms",
                {
                    "RN": player_name,
                    "MH": sms_title,
                    "TXT": sms_text
                }
            )
            if sync:
                response = await self.wait_for_response("sms")
                return response
            return True

        except Exception as e:
            logger.error(e)
            
            
    async def delete_message(self, message_id, sync = True):
        
        try:
            
            await self.send_json_message(
                "dms", {
                    "MID": message_id
                }
            )
            
            if sync:
                response = self.wait_for_response("dms")
                return response
            logger.info(f'Message {message_id} removed!')
            return True
            
        except Exception as e:
            logger.error(e) 
            return False
        
        
        
    async def no_battle_handle(self, data):
        
        msg_data = data.get("MSG", [])
        for msg_detail in msg_data:
            if msg_detail[1] == 67:
                await self.delete_message(msg_detail[0])
    
    