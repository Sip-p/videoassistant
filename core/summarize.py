# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.runnables import RunnablePassthrough,RunnableLambda
# from dotenv import load_dotenv
# import os

# load_dotenv()

 

# def get_llm():
#     return ChatGroq(
#     model="openai/gpt-oss-120b",
#     temperature=0.3,
#     api_key=os.getenv("GROQ_API_KEY")
# )


# def split_transcript(transcript:str)->list:
#     splitter=RecursiveCharacterTextSplitter(
#         chunk_size=3000,
#         chunk_overlap=200,
#     )

#     return splitter.split_text(transcript)

# def summarize(transcript:str)->str:
#     llm=get_llm()
#     map_prompt=ChatPromptTemplate.from_messages([
#         ("system", "Summarize this portion of a meeting transcript concisely."),
#         ("human","{text}"),
#     ])

#     map_chain=map_prompt |llm |StrOutputParser()

#     chunks=split_transcript(transcript)
#     chunk_summaries=[map_chain.invoke({"text":chunk}) for chunk in chunks]


#     combined="\n\n.join(chunk_summaries)"

#     combined_prompt=ChatPromptTemplate.from_messages(
#         [
#             {"system",
#              "You are an expert meeting summarizer.Combine these partial summaries"
#              "into one final professional meeting summary in bullet points."
#              },
#              {"human","{text}"},
#         ]
#     )


#     combined_chain=(
#         RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) |combined_prompt |llm |StrOutputParser
#     )

#     return combined_chain.invoke(combined)


# def generate_title(transcript:str)->str:
#     llm=get_llm()
#     title_chain=(
#         RunnablePassthrough() |RunnableLambda(lambda s:{"text":s}) |
#         ChatPromptTemplate.from_messages(
#             [
#                 ("system",
#                 "Based on the meeting transcript, generate a short professional meeting title"
#                 "(max 8 words). Only return the title nothing else"),
#                 ("human","{text}"),
#             ]
#         )
#         | llm |StrOutputParser()
#     )

#     return title_chain.invoke(transcript[:2000])




from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()


def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )


def split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )

    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    if not transcript.strip():
        return "No transcript available to summarize."

    llm = get_llm()

    # MAP: Summarize each transcript chunk
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}")
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = tuple(
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    )

    # Combine partial summaries
    combined = "\n\n".join(chunk_summaries)

    # REDUCE: Generate one final summary
    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting summarizer.
            Combine these partial summaries into one final,
            professional meeting summary in clear bullet points."""
        ),
        ("human", "{text}")
    ])

    combined_chain = combined_prompt | llm | StrOutputParser()

    return combined_chain.invoke({"text": combined})


def generate_title(transcript: str) -> str:
    llm = get_llm()

    title_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Based on the meeting transcript, generate a short
            professional meeting title (maximum 8 words).
            Only return the title, nothing else."""
        ),
        ("human", "{text}")
    ])

    title_chain = title_prompt | llm | StrOutputParser()

    return title_chain.invoke({"text": transcript[:2000]})
