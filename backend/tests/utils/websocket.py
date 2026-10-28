def check_message_info(received_message, sender_id, room_id, content):
    assert "id" in received_message
    assert "created_at" in received_message
    assert "sender_id" in received_message
    assert "content" in received_message
    assert "room_id" in received_message
    assert received_message["sender_id"] == sender_id 
    assert received_message["content"] == content 
    assert received_message["room_id"] == room_id 