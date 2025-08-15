import asyncio
import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

load_dotenv()

class InteractiveHashnodeAgent:
    def __init__(self):
        # Load initial env (may contain placeholders)
        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        
        # Hashnode configuration placeholders
        self.hashnode_username = os.getenv("HASHNODE_USERNAME")
        self.hashnode_hostname = os.getenv("HASHNODE_HOSTNAME")
        self.hashnode_token = os.getenv("HASHNODE_PERSONAL_ACCESS_TOKEN")
        
        # Groq key placeholder
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        self.llm = None
        self.agent = None
        self.conversation_history = []
    
    def _is_placeholder(self, value: str) -> bool:
        if not value:
            return True
        lowered = value.strip().lower()
        return (
            lowered.startswith("your_") or
            lowered.endswith("_here") or
            " " in value.strip()
        )
    
    def _write_env(self, key: str, value: str) -> None:
        # Read existing lines
        env_lines = []
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        mapping = {}
        for line in env_lines:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                mapping[k.strip()] = v.rstrip("\n")
        mapping[key] = value
        # Write back
        with open(self.env_path, "w", encoding="utf-8") as f:
            for k, v in mapping.items():
                f.write(f"{k}={v}\n")
        
    def _ensure_config(self):
        print("\n🔑 Configuration check...")
        # GROQ_API_KEY
        while self._is_placeholder(self.groq_api_key):
            print("GROQ_API_KEY is missing/invalid. Enter your Groq API key (no spaces):")
            self.groq_api_key = input("> ").strip()
            if self._is_placeholder(self.groq_api_key):
                print("Invalid value. Please try again.")
            else:
                self._write_env("GROQ_API_KEY", self.groq_api_key)
        
        # HASHNODE_PERSONAL_ACCESS_TOKEN
        while self._is_placeholder(self.hashnode_token):
            print("HASHNODE_PERSONAL_ACCESS_TOKEN is missing/invalid. Paste your Hashnode token:")
            self.hashnode_token = input("> ").strip()
            if self._is_placeholder(self.hashnode_token):
                print("Invalid value. Please try again.")
            else:
                self._write_env("HASHNODE_PERSONAL_ACCESS_TOKEN", self.hashnode_token)
        
        # HASHNODE_USERNAME (handle, no spaces)
        while self._is_placeholder(self.hashnode_username):
            print("HASHNODE_USERNAME is missing/invalid. Enter your Hashnode handle (no spaces), e.g. 'samsuljahith':")
            self.hashnode_username = input("> ").strip()
            if self._is_placeholder(self.hashnode_username):
                print("Invalid value. Please try again.")
            else:
                self._write_env("HASHNODE_USERNAME", self.hashnode_username)
        
        # HASHNODE_HOSTNAME (domain-like, no spaces)
        while self._is_placeholder(self.hashnode_hostname):
            print("HASHNODE_HOSTNAME is missing/invalid. Enter your blog hostname (no spaces), e.g. 'blog.yourname.hashnode.dev' or your custom domain:")
            self.hashnode_hostname = input("> ").strip()
            if self._is_placeholder(self.hashnode_hostname):
                print("Invalid value. Please try again.")
            else:
                self._write_env("HASHNODE_HOSTNAME", self.hashnode_hostname)
        
        # Reload env after updates
        load_dotenv(override=True)
    
    async def setup_agent(self):
        """Set up the MCP client and agent"""
        try:
            # Ensure config before creating LLM
            self._ensure_config()
            
            # Create LLM with low temperature to avoid tool hallucinations
            self.llm = ChatGroq(
                temperature=0,
                groq_api_key=self.groq_api_key,
                model_name="llama-3.1-8b-instant"
            )
            
            print("🔧 Setting up Hashnode MCP client...")
            
            # Get the absolute path to the run_server.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = os.path.join(current_dir, "..", "hashnode-mcp-server", "run_server.py")
            
            client = MultiServerMCPClient({
                "hashnode": {
                    "command": "python",
                    "args": [server_path],
                    "transport": "stdio",
                }
            })
            
            tools = await client.get_tools()
            print(f"✅ Found {len(tools)} Hashnode tools available")
            
            self.agent = create_react_agent(self.llm, tools)
            print("✅ Agent setup complete!")
            
        except Exception as e:
            print(f"❌ Error setting up agent: {str(e)}")
            print("Make sure the Hashnode MCP server is running")
            return False
        
        return True
    
    def print_welcome(self):
        """Print welcome message and available commands"""
        print("\n" + "="*60)
        print("🚀 Welcome to Interactive Hashnode Agent!")
        print("="*60)
        
        # Show configuration status
        print("\n📋 Configuration Status:")
        print("✅ Hashnode API Token: Configured")
        print(f"✅ Hashnode Username: {self.hashnode_username}")
        print(f"✅ Hashnode Hostname: {self.hashnode_hostname}")
        
        print("\nI can help you with various Hashnode tasks:")
        print("• Create and publish articles")
        print("• Update existing articles")
        print("• Search for articles")
        print("• Get article details")
        print("• Get user information")
        print("• Get latest articles from publications")
        print("• Test API connection")
        
        print("\n💡 Example commands:")
        print("• 'Create a blog post about Python programming'")
        print("• 'Search for articles about AI'")
        print("• 'Get my latest articles'")
        print("• 'Update my article with new content'")
        print("• 'Test the API connection'")
        print("• 'Show my Hashnode profile'")
        
        print("\n📝 Special commands:")
        print("• 'help' - Show this help message")
        print("• 'config' - Show current configuration")
        print("• 'setup' - Help with configuration setup")
        print("• 'history' - Show conversation history")
        print("• 'clear' - Clear conversation history")
        print("• 'quit' or 'exit' - Exit the agent")
        print("="*60)
    
    def show_config(self):
        """Show current configuration"""
        print("\n📋 Current Configuration:")
        print("-" * 40)
        print("Hashnode API Token: ✅ Set")
        print(f"Hashnode Username: {self.hashnode_username}")
        print(f"Hashnode Hostname: {self.hashnode_hostname}")
    
    def show_setup_help(self):
        """Show setup help"""
        print("\n🔧 Setup Instructions:")
        print("-" * 40)
        print("1. Get your Hashnode Personal Access Token:")
        print("   - Go to https://hashnode.com/settings/developer")
        print("   - Create a new Personal Access Token")
        print("   - Copy the token")
        
        print("\n2. Find your Hashnode username:")
        print("   - Go to your Hashnode profile")
        print("   - Your username is in the URL: https://hashnode.com/@your_username")
        
        print("\n3. Find your blog hostname:")
        print("   - Go to your blog settings")
        print("   - Look for the custom domain or default hostname")
        print("   - Example: blog.yourname.hashnode.dev")
        
        print("\n4. Add to your .env file:")
        print("HASHNODE_PERSONAL_ACCESS_TOKEN=your_token_here")
        print("HASHNODE_USERNAME=your_username_here")
        print("HASHNODE_HOSTNAME=your_blog_hostname_here")
        
        print("\n5. Restart the agent")
    
    def get_user_input(self):
        """Get user input with a nice prompt"""
        try:
            user_input = input("\n🤖 What would you like me to help you with? > ").strip()
            return user_input
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Hashnode Agent!")
            return "quit"
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for using Hashnode Agent!")
            return "quit"
    
    async def process_command(self, user_input):
        """Process user commands and special actions"""
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye! Thanks for using Hashnode Agent!")
            return False
        
        elif user_input.lower() == 'help':
            self.print_welcome()
            return True
        
        elif user_input.lower() == 'config':
            self.show_config()
            return True
        
        elif user_input.lower() == 'setup':
            self.show_setup_help()
            return True
        
        elif user_input.lower() == 'history':
            self.show_history()
            return True
        
        elif user_input.lower() == 'clear':
            self.conversation_history = []
            print("✅ Conversation history cleared!")
            return True
        
        elif user_input.lower() == '':
            print("Please enter a command or type 'help' for assistance.")
            return True
        
        else:
            # Process as a regular task
            return await self.process_task(user_input)
    
    async def process_task(self, user_input):
        """Process a regular task using the agent"""
        try:
            print(f"\n🔄 Processing: {user_input}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Create enhanced prompt with user's Hashnode info and strict tool usage instruction
            instruction = (
                "You are a Hashnode assistant. Use ONLY these tools when needed: "
                "test_api_connection, create_article, update_article, get_latest_articles, "
                "search_articles, get_article_details, get_user_info. Do NOT invent other tools."
            )
            
            # Normalize some intents to explicit tool usage with configured identifiers
            normalized_input = user_input
            if "show my" in user_input.lower() and "profile" in user_input.lower():
                normalized_input = f"Get user info for username '{self.hashnode_username}'."
            if "my latest articles" in user_input.lower():
                normalized_input = (
                    f"Get latest articles for hostname '{self.hashnode_hostname}' with a sensible limit."
                )
            
            enhanced_prompt = normalized_input + (
                f"\n\nNote: My Hashnode username is '{self.hashnode_username}' and my blog hostname is "
                f"'{self.hashnode_hostname}'."
            )
            
            # Create messages for the agent
            messages = [
                SystemMessage(content=instruction),
                HumanMessage(content=enhanced_prompt)
            ]
            
            # Get response from agent
            response = await self.agent.ainvoke({"messages": messages})
            
            # Extract the final response
            if hasattr(response, 'messages') and response.messages:
                final_message = response.messages[-1]
                if hasattr(final_message, 'content'):
                    agent_response = final_message.content
                else:
                    agent_response = str(final_message)
            else:
                agent_response = str(response)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": agent_response})
            
            # Print the response
            print(f"\n✅ Task completed!")
            print(f"📝 Response: {agent_response}")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Error processing task: {str(e)}"
            print(error_msg)
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return True
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 Conversation History:")
        print("-" * 40)
        for i, message in enumerate(self.conversation_history, 1):
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                print(f"{i}. 👤 You: {content}")
            else:
                print(f"{i}. 🤖 Agent: {content}")
            print()
    
    async def run(self):
        """Main run loop for the interactive agent"""
        print("🚀 Starting Interactive Hashnode Agent...")
        
        # Setup the agent (includes config wizard and LLM init)
        if not await self.setup_agent():
            return
        
        # Show welcome message
        self.hashnode_username = os.getenv("HASHNODE_USERNAME")
        self.hashnode_hostname = os.getenv("HASHNODE_HOSTNAME")
        self.hashnode_token = os.getenv("HASHNODE_PERSONAL_ACCESS_TOKEN")
        self.print_welcome()
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Process the command
                should_continue = await self.process_command(user_input)
                
                if not should_continue:
                    break
                
                # Ask if there's anything else
                print("\n" + "-" * 40)
                print("🤔 Is there anything else I can help you with?")
                print("(Type 'help' for commands, 'quit' to exit)")
                
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Let's continue...")

async def main():
    """Main entry point"""
    agent = InteractiveHashnodeAgent()
    await agent.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Hashnode Agent!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("Please check your configuration and try again.")
