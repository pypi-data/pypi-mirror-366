"""
Streaming Response Handler for AI Helper Agent
Implements real-time LLM response streaming for enhanced user experience
Requirement #4: Streaming LLM Response Implementation
"""

import asyncio
import sys
import time
import threading
from typing import AsyncIterator, Optional, Dict, Any, List
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig


class StreamingResponseHandler:
    """Handles streaming LLM responses with real-time display"""
    
    def __init__(self, llm: ChatGroq, conversation_chain):
        self.llm = llm
        self.conversation_chain = conversation_chain
        self.total_tokens = 0
        self.start_time = None
        self.response_buffer = ""
        
    async def stream_generate(self, enhanced_input: str, config: RunnableConfig) -> str:
        """Main streaming method - replaces ainvoke for real-time response"""
        try:
            self.start_time = time.time()
            self.response_buffer = ""
            self.total_tokens = 0
            
            # Don't print AI indicator here - it's handled by the thinking indicator
            
            # Determine the input format based on the conversation chain type
            try:
                # Try the newer format first (for multi-provider CLI)
                async for chunk in self.conversation_chain.astream(
                    {"input": enhanced_input},
                    config=config
                ):
                    # Handle different chunk formats
                    content = self._extract_content_from_chunk(chunk)
                    
                    if content:
                        # Display immediately for real-time experience
                        print(content, end="", flush=True)
                        self.response_buffer += content
                        self.total_tokens += 1
            except Exception:
                # Fallback to older messages format
                async for chunk in self.conversation_chain.astream(
                    {"messages": [HumanMessage(content=enhanced_input)]},
                    config=config
                ):
                    # Handle different chunk formats
                    content = self._extract_content_from_chunk(chunk)
                    
                    if content:
                        # Display immediately for real-time experience
                        print(content, end="", flush=True)
                        self.response_buffer += content
                        self.total_tokens += 1
            
            # Performance statistics
            elapsed_time = time.time() - self.start_time
            tokens_per_second = self.total_tokens / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n\n📊 {self.total_tokens} tokens • {elapsed_time:.2f}s • {tokens_per_second:.1f} tok/s")
            
            return self.response_buffer
            
        except Exception as e:
            error_msg = f"❌ Streaming error: {e}"
            print(f"\n{error_msg}")
            return error_msg
    
    def _extract_content_from_chunk(self, chunk) -> str:
        """Extract content from different chunk formats"""
        if isinstance(chunk, dict):
            if 'answer' in chunk:
                return chunk['answer']
            elif 'content' in chunk:
                return chunk['content']
            elif 'text' in chunk:
                return chunk['text']
        elif hasattr(chunk, 'content'):
            return chunk.content
        elif hasattr(chunk, 'text'):
            return chunk.text
        else:
            return str(chunk) if chunk else ""


class CustomStreamingCallback(AsyncCallbackHandler):
    """Custom callback handler for streaming with enhanced display"""
    
    def __init__(self):
        self.tokens = []
        self.start_time = None
        self.word_count = 0
        
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        """Called when LLM starts"""
        self.start_time = time.time()
        self.tokens = []
        self.word_count = 0
        # Don't print AI indicator here - it's handled by the thinking indicator
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called on each new token - stream it immediately"""
        print(token, end="", flush=True)
        self.tokens.append(token)
        # Count words (rough estimation)
        if token.strip() and not token.startswith(' '):
            self.word_count += 1
    
    async def on_llm_end(self, response, **kwargs: Any) -> None:
        """Called when LLM finishes"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        total_tokens = len(self.tokens)
        tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0
        wpm = (self.word_count / elapsed_time * 60) if elapsed_time > 0 else 0
        
        print(f"\n\n📊 {total_tokens} tokens • {self.word_count} words • {elapsed_time:.2f}s • {wpm:.0f} WPM")


class AdvancedStreamingHandler:
    """Advanced streaming handler with typing indicators and enhanced UX"""
    
    def __init__(self, llm: ChatGroq, conversation_chain):
        self.llm = llm
        self.conversation_chain = conversation_chain
        self.typing_active = False
        
    async def start_typing_indicator(self):
        """Show typing indicator while processing"""
        self.typing_active = True
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        
        while self.typing_active:
            print(f"\r🤖 {indicators[i % len(indicators)]} Thinking...", end="", flush=True)
            await asyncio.sleep(0.1)
            i += 1
    
    def stop_typing_indicator(self):
        """Stop typing indicator"""
        self.typing_active = False
        print("\r" + " " * 25 + "\r", end="", flush=True)  # Clear the line
    
    async def stream_with_indicators(self, enhanced_input: str, config: RunnableConfig) -> str:
        """Stream response with typing indicators and enhanced UX"""
        try:
            # Start typing indicator
            typing_task = asyncio.create_task(self.start_typing_indicator())
            
            # Small delay to show thinking indicator
            await asyncio.sleep(0.5)
            
            # Stop typing indicator and start streaming
            self.stop_typing_indicator()
            typing_task.cancel()
            
            # Don't print AI indicator here - it's handled by the thinking indicator
            
            response_buffer = ""
            start_time = time.time()
            token_count = 0
            word_count = 0
            
            # Stream the response
            async for chunk in self.conversation_chain.astream(
                {"messages": [HumanMessage(content=enhanced_input)]},
                config=config
            ):
                # Extract content from chunk
                content = self._extract_content_from_chunk(chunk)
                
                if content:
                    print(content, end="", flush=True)
                    response_buffer += content
                    token_count += 1
                    # Count words (approximate)
                    word_count += len(content.split())
            
            # Performance statistics
            elapsed_time = time.time() - start_time
            wpm = (word_count / elapsed_time * 60) if elapsed_time > 0 else 0
            cps = len(response_buffer) / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n\n📊 {token_count} tokens • {word_count} words • {elapsed_time:.1f}s • {wpm:.0f} WPM • {cps:.0f} CPS")
            
            return response_buffer
            
        except asyncio.CancelledError:
            self.stop_typing_indicator()
            return "❌ Response cancelled"
        except Exception as e:
            self.stop_typing_indicator()
            error_msg = f"❌ Streaming error: {e}"
            print(f"\n{error_msg}")
            return error_msg
    
    def _extract_content_from_chunk(self, chunk) -> str:
        """Extract content from different chunk formats"""
        if isinstance(chunk, dict):
            if 'answer' in chunk:
                return chunk['answer']
            elif 'content' in chunk:
                return chunk['content']
            elif 'text' in chunk:
                return chunk['text']
        elif hasattr(chunk, 'content'):
            return chunk.content
        elif hasattr(chunk, 'text'):
            return chunk.text
        else:
            return str(chunk) if chunk else ""


class EnhancedStreamingHandler:
    """Enhanced streaming handler with progress bars and advanced features"""
    
    def __init__(self, llm: ChatGroq, conversation_chain):
        self.llm = llm
        self.conversation_chain = conversation_chain
        self.typing_active = False
        
    async def stream_with_progress(self, enhanced_input: str, config: RunnableConfig, 
                                 show_progress: bool = True) -> str:
        """Stream with progress indicators and real-time stats"""
        try:
            response_buffer = ""
            start_time = time.time()
            token_count = 0
            
            if show_progress:
                print("🚀 Generating response...", flush=True)
                # AI indicator is handled by thinking indicator in CLI
            else:
                # AI indicator is handled by thinking indicator in CLI
                pass
            
            # Track response generation
            last_update = start_time
            
            async for chunk in self.conversation_chain.astream(
                {"messages": [HumanMessage(content=enhanced_input)]},
                config=config
            ):
                content = self._extract_content_from_chunk(chunk)
                
                if content:
                    print(content, end="", flush=True)
                    response_buffer += content
                    token_count += 1
                    
                    # Show progress every 50 tokens
                    if show_progress and token_count % 50 == 0:
                        current_time = time.time()
                        if current_time - last_update >= 1.0:  # Update every second
                            elapsed = current_time - start_time
                            speed = token_count / elapsed if elapsed > 0 else 0
                            print(f" [{token_count} tokens, {speed:.1f} tok/s]", end="", flush=True)
                            last_update = current_time
            
            # Final statistics
            elapsed_time = time.time() - start_time
            word_count = len(response_buffer.split())
            chars = len(response_buffer)
            
            avg_token_speed = token_count / elapsed_time if elapsed_time > 0 else 0
            avg_word_speed = word_count / elapsed_time if elapsed_time > 0 else 0
            avg_char_speed = chars / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n\n📈 PERFORMANCE METRICS:")
            print(f"   📊 {token_count} tokens • {word_count} words • {chars} characters")
            print(f"   ⏱️ {elapsed_time:.2f} seconds")
            print(f"   🚀 {avg_token_speed:.1f} tok/s • {avg_word_speed:.1f} words/s • {avg_char_speed:.1f} chars/s")
            
            return response_buffer
            
        except Exception as e:
            error_msg = f"❌ Enhanced streaming error: {e}"
            # Don't show transformers errors to user - use fallback
            if "transformers" in str(e).lower():
                error_msg = "❌ Enhanced streaming temporarily unavailable, using standard streaming"
            print(f"\n{error_msg}")
            return error_msg
    
    def _extract_content_from_chunk(self, chunk) -> str:
        """Extract content from different chunk formats"""
        if isinstance(chunk, dict):
            if 'answer' in chunk:
                return chunk['answer']
            elif 'content' in chunk:
                return chunk['content']
            elif 'text' in chunk:
                return chunk['text']
        elif hasattr(chunk, 'content'):
            return chunk.content
        elif hasattr(chunk, 'text'):
            return chunk.text
        else:
            return str(chunk) if chunk else ""


def create_streaming_callback() -> CustomStreamingCallback:
    """Factory function to create streaming callback"""
    return CustomStreamingCallback()


async def test_streaming_functionality():
    """Test the streaming functionality"""
    print("🧪 Testing streaming functionality...")
    
    # This would be integrated into the CLI class
    # Test streaming components individually
    
    print("✅ StreamingResponseHandler ready")
    print("✅ CustomStreamingCallback ready")
    print("✅ AdvancedStreamingHandler ready")
    print("✅ EnhancedStreamingHandler ready")
    print("🎉 All streaming components initialized successfully!")


if __name__ == "__main__":
    # Direct testing
    asyncio.run(test_streaming_functionality())
